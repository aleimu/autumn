# coding:utf-8

import time
import json
import datetime

import tornado
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.concurrent import run_on_executor
from tornado import gen
from tornado.options import define, options, parse_command_line
from collections import deque
# 这个并发库在python3自带;在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor

define("port", default=8888, type=int)

settings = {"static_path": "template"}


class just_now_router(RequestHandler):
    def get(self):
        self.write("i hope just now see you")


class sleep_long_time_router(RequestHandler):
    def get(self):
        time.sleep(60)
        self.write("sleep 60s")


class index_router(RequestHandler):
    def get(self):
        title1 = ''
        try:
            title1 = self.get_argument("text1")
        except:
            self.render("./templates/tailf_index.html", textDiv="")
        if title1:
            self.render("./templates/tailf_index.html", textDiv="textDiv")


class sleep_async_router(RequestHandler):
    executor = ThreadPoolExecutor(2)

    def get(self):
        # 在执行add_callback方法后马上就会执行下一行代码，而callback函数将在下一轮事件循环中才调用，从而就能实现延迟任务。
        # 当有一些耗时操作并不需要返回给请求方时，就可以采用延迟任务的形式，比如发送提醒邮件。
        IOLoop.instance().add_callback(self.sleep)
        self.write("when i sleep")
        return

    @run_on_executor
    def sleep(self):
        print("sleep1 start", datetime.datetime.now())
        time.sleep(5)
        print("sleep1 end", datetime.datetime.now())


class sleep_coroutine_router(RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        print("sleep2 start", datetime.datetime.now())
        tornado.gen.sleep(5)
        # sleep(5)
        self.write("after sleep, now I'm back %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print("sleep2 end", datetime.datetime.now())


class sleep_router(RequestHandler):
    executor = ThreadPoolExecutor(10)

    @run_on_executor
    def get(self):
        print("sleep3 start", datetime.datetime.now())
        time.sleep(5)
        self.write("after sleep, now I'm back %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print("sleep3 end", datetime.datetime.now())


class wait_router(RequestHandler):
    executor = ThreadPoolExecutor(2)

    @tornado.gen.coroutine
    def get(self):
        result, m = yield tornado.gen.maybe_future(self.wait())
        yield self.write({"result": result, "sum": m})

    @run_on_executor
    def wait(self):
        time.sleep(5)
        return "success", (4, 5, 6)  # 不要 yield 4,5,6


class chat_index_router(RequestHandler):
    def get(self):
        self.render("./templates/chat_index.html")


class chat_room_router(WebSocketHandler):
    users = set()  # 用来存放在线用户的容器

    def open(self):
        self.users.add(self)  # 建立连接后添加用户到容器中
        for u in self.users:  # 向已在线用户发送消息
            u.write_message(
                u"[%s]-[%s]-进入聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def on_message(self, message):
        for u in self.users:  # 向在线用户广播消息
            u.write_message(u"[%s]-[%s]-说：%s" % (
                self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))

    def on_close(self):
        self.users.remove(self)  # 用户关闭连接后从容器中移除用户
        for u in self.users:
            u.write_message(
                u"[%s]-[%s]-离开聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求


class tailf_router(WebSocketHandler):

    def open(self, *args):
        print("WebSocket opened")

    def on_message(self, message):
        def tail(filename, n=10):
            'Return the last n lines of a file'
            while True:
                lines = '<br>'.join(list(deque(open(filename), n)))
                print("lines:", lines)
                self.write_message(lines)
                if lines:
                    time.sleep(0.5)
                if "Control-C" in lines:
                    self.close()
                    break

        tail('ip.txt')

    def on_close(self):
        print("WebSocket closed")


class send_router(WebSocketHandler):
    clients = set()

    def open(self):
        send_router.clients.add(self)
        self.write_message(json.dumps({'input': 'connected...'}))
        self.stream.set_nodelay(True)

    def on_message(self, message):
        message = json.loads(message)
        self.write_message(json.dumps({'input': 'response...'}))
        i = 0
        while i <= 10:
            i += 1
            self.write_message(json.dumps(message))
            time.sleep(1)
        # 服务器主动关闭
        self.close()
        send_router.clients.remove(self)

    def on_close(self):
        # 客户端主动关闭
        send_router.clients.remove(self)


app = tornado.web.Application([
    (r'/', index_router),
    (r'/text1', index_router),
    (r"/justnow", just_now_router),
    (r"/sleep60", sleep_long_time_router),
    (r"/wait", wait_router),
    (r'/ws', tailf_router),
    (r'/sleep1', sleep_async_router),
    (r'/sleep2', sleep_coroutine_router),
    (r'/sleep3', sleep_router),
    (r'/send', send_router),
    (r'/into_chat', chat_index_router),
    (r'/chat', chat_room_router),
], **settings)

if __name__ == '__main__':
    app.listen(options.port)
    IOLoop.instance().start()

# 还是那句话:既然选择异步,那就全流程都得异步.
