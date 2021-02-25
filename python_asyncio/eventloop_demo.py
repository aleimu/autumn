import collections

_event_loop = None


def get_event_loop():
    global _event_loop
    if _event_loop is None:
        _event_loop = Eventloop()
    return _event_loop


class Future:
    _FINISHED = 'finished'
    _PENDING = 'pending'
    _CANCELLED = 'CANCELLED'

    def __init__(self, loop=None):
        if loop is None:
            self._loop = get_event_loop()  # 获取当前的 eventloop
        else:
            self._loop = loop
        self._callbacks = []
        self.status = self._PENDING
        self._blocking = False
        self._result = None

    def _schedule_callbacks(self):
        # 将回调函数添加到事件队列里，eventloop 稍后会运行
        for callbacks in self._callbacks:
            self._loop.add_ready(callbacks)
        self._callbacks = []

    def set_result(self, result):
        self.status = self._FINISHED
        self._result = result
        self._schedule_callbacks()  # future 完成后，执行回调函数

    def add_done_callback(self, callback, *args):
        # 为 future 增加回调函数
        if self.done():
            self._loop.call_soon(callback, *args)
        else:
            handle = Handle(callback, self._loop, *args)
            self._callbacks.append(handle)

    def done(self):
        return self.status != self._PENDING

    def result(self):
        if self.status != self._FINISHED:
            raise RuntimeError('future is not ready')
        return self._result

    def __iter__(self):
        if not self.done():
            self._blocking = True
        yield self
        assert self.done(), 'future not done'
        return self.result()


class Task(Future):

    def __init__(self, coro, loop=None):
        super().__init__(loop=loop)
        self._coro = coro  # 协程
        self._loop.call_soon(self._step)  # 启动协程

    def _step(self, exc=None):
        try:
            if exc is None:
                result = self._coro.send(None)
            else:
                result = self._coro.throw(exc)  # 有异常，则抛出异常
        except StopIteration as exc:  # 说明协程已经执行完毕，为协程设置值
            self.set_result(exc.value)
        else:
            if isinstance(result, Future):
                if result._blocking:
                    self._blocking = False
                    result.add_done_callback(self._wakeup, result)
                else:
                    self._loop.call_soon(
                        self._step, RuntimeError('你是不是用了 yield 才导致这个error?')
                    )
            elif result is None:
                self._loop.call_soon(self._step)
            else:
                self._loop.call_soon(self._step, RuntimeError('你产生了一个不合规范的值'))

    def _wakeup(self, future):
        try:
            future.result()  # 查看future 运行是否有异常
        except Exception as exc:
            self._step(exc)
        else:
            self._step()


class Eventloop:

    def __init__(self):
        self._ready = collections.deque()  # 事件队列
        self._stopping = False

    def stop(self):
        self._stopping = True

    def call_soon(self, callback, *args):
        # 将事件添加到队列里
        handle = Handle(callback, self, *args)
        self._ready.append(handle)

    def add_ready(self, handle):
        # 将事件添加到队列里
        if isinstance(handle, Handle):
            self._ready.append(handle)
        else:
            raise RuntimeError('only handle is allowed to join in ready')

    def run_once(self):
        # 执行队列里的事件
        ntodo = len(self._ready)
        for i in range(ntodo):
            handle = self._ready.popleft()
            handle._run()

    def run_forever(self):
        while True:
            self.run_once()
            if self._stopping:
                break


class Handle:

    def __init__(self, callback, loop, *args):
        self._callback = callback
        self._args = args

    def _run(self):
        self._callback(*self._args)
