import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

selector = DefaultSelector()
stopped = False
urls_todo = {"/", "/1", "/2", "/3"}
urls_todo = {"/"}


# Task, Future, Coroutine三者精妙地串联在一起

# 结果保存，每一个处需要异步的地方都会调用，保持状态和callback
# 程序得知道当前所处的状态，而且要将这个状态在不同的回调之间延续下去。
class Future:
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

    def __iter__(self):
        """
        yield的出现使得__iter__函数变成一个生成器，生成器本身就有next方法，所以不需要额外实现。
        yield from x语句首先调用iter(x)获取一个迭代器（生成器也是迭代器）
        """
        yield self  # 外面使用yield from把f实例本身返回
        return self.result  # 在Task.step中send(result)的时候再次调用这个生成器，但是此时会抛出stopInteration异常，并且把self.result返回


# 激活包装的生成器，以及在生成器yield后恢复执行继续下面的代码
class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)  # 激活Task包裹的生成器

    def step(self, future):
        try:
            # next_future = self.coro.send(future.result)
            next_future = self.coro.send(None)  # 驱动future
            # next_future = future.send(None)  # 错误的
        except StopIteration:
            return

        next_future.add_done_callback(self.step)  # 重点 给future对象添加下次运行的callback


# 异步就是可以暂定的函数，函数间切换的调度靠事件循环,yield 正好可以中断函数运行

class Crawler:
    def __init__(self, url):
        self.url = url
        self.response = b""

    def fetch(self):
        global stopped
        sock = socket.socket()
        yield from connect(sock, ("xkcd.com", 80))
        get = "GET {0} HTTP/1.0\r\nHost:xkcd.com\r\n\r\n".format(self.url)
        sock.send(get.encode('ascii'))
        self.response = yield from read_all(sock)
        print(self.response)
        urls_todo.remove(self.url)
        if not urls_todo:
            stopped = True


def connect(sock, address):
    f = Future()
    sock.setblocking(False)
    try:
        sock.connect(address)
    except BlockingIOError:
        pass

    def on_connected():
        f.set_result(None)

    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    yield from f
    selector.unregister(sock.fileno())


def read(sock):
    f = Future()

    def on_readable():
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)  # 注册一个文件对象以监听其IO事件;
    """
    此处的chunck接收的是f中return的f.result，同时会跑出一个stopIteration的异常，只不过被yield from处理了。
    这里也可直接写成chunck = yiled f
    """
    chunck = yield from f
    selector.unregister(sock.fileno())  # 从selection中注销文件对象, 即从监听列表中移除它; 文件对象应该在关闭前注销.
    return chunck


def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)   # yield from来解决生成器里玩生成器的问题
    return b"".join(response)


# 事件驱动，让所有之前注册的callback运行起来
def loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()


"""
无链式调用
selector的回调里只管给future设置值，不再关心业务逻辑
loop 内回调callback()不再关注是谁触发了事件,因为协程能够保存自己的状态，知道自己的future是哪个。也不用关心到底要设置什么值，因为要设置什么值也是协程内安排的。
已趋近于同步代码的结构
无需程序员在多个协程之间维护状态，例如哪个才是自己的sock
"""

if __name__ == "__main__":
    import time

    start = time.time()
    for url in urls_todo:
        crawler = Crawler(url)
        Task(crawler.fetch())  # 将各生成器和对应的callback注册到事件循环loop中，并激活生成器
    loop()
    print(time.time() - start)

"""
1.创建Crawler 实例；
2.调用fetch方法，会创建socket连接和在selector上注册可写事件；
3.fetch内并无阻塞操作，该方法立即返回；
4.重复上述3个步骤，将10个不同的下载任务都加入事件循环；
5.启动事件循环，进入第1轮循环，阻塞在事件监听上；
6.当某个下载任务EVENT_WRITE被触发，回调其connected方法，第一轮事件循环结束；
7.进入第2轮事件循环，当某个下载任务有事件触发，执行其回调函数；此时已经不能推测是哪个事件发生，因为有可能是上次connected里的EVENT_READ先被触发，也可能是其他某个任务的EVENT_WRITE被触发；（此时，原来在一个下载任务上会阻塞的那段时间被利用起来执行另一个下载任务了）
8.循环往复，直至所有下载任务被处理完成
9.退出事件循环，结束整个下载程序
"""
