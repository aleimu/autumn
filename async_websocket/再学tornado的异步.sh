# tornado 是单线程的

# 部署服务应该通过Nginx代理多个tornado服务起的多个port. 参考 http://demo.pythoner.com/itt2zh/ch8.html

# tornado如何实现异步websocket推送？
{
在实现一个websocket的推送，主要就是后端推送pub/sub了redis的信息到前端。然而自己实现的推送开了两个chrome tab就有一个一直pending，可我明明在redis阻塞的部分用了gen.coroutine，一直不明白。想请问一下如何改进？

最近一直在研究Tornado异步操作，然而一番研究后发现要使一个函数异步化的最好方法就是采用相关异步库，但目前很多功能强大的库都不在此列。经过一番查找文档和搜索示范，终于发现了ThreadPoolExecutor模块和run_on_executor装饰器。用法就是建立线程池，用run_on_executor装饰的函数即运行在其中线程中，从而从主线程中分离出来，达到异步的目的。

gen.coroutine的意义，这个装饰器其实并不能让阻塞代码变成非阻塞，而是将本身需要异步回调的代码写成同步风格。它并不能改变什么，而是让你可以换一种代码风格增强代码可读性。整个tornado生态是基于它IOLoop的，所以不是拿到任何异步库都能直接使用，我们都知道异步是基于事件的，而事件的通知管理则是依靠事件轮询设施eventloop的它通常构建于select、epoll、kq，这个IOloop就是事件轮询设施，一切不能被它接纳的异步库都是无法集成到tornado的。所以如果你想把redis集成到tornado就必须是IOLoop能够接纳的非阻塞redis https://pypi.org/project/tornado-redis/2.4.2/

it.next() 仍然是阻塞的，Tornado 的异步模型应该是在你的 while True 里面 item = yield 一个future 才对，虽然你 yield 了一个 Task，但是这个 Task 本身不是异步的（等待的时候不能被打断，不能将控制权交给IOLoop）。

如果后端有查询实在是太慢，无法绕过，Tornaod的建议是将这些查询在后端封装独立封装成为HTTP接口，然后使用Tornado内置的异步HTTP客户端进行调用。
}

# 什么是WS/WSS？
{
WebSocket (WS)是HTML5一种新的协议。它实现了浏览器与服务器全双工通信，能更好地节省服务器资源和带宽并达到实时通讯。WebSocket建立在TCP之上，同HTTP一样通过TCP来传输数据，但是它和HTTP最大不同是：
WebSocket是一种双向通信协议，在建立连接后，WebSocket服务器和Browser/Client Agent都能主动的向对方发送或接收数据，就像Socket一样；WebSocket需要类似TCP的客户端和服务器端通过握手连接，连接成功后才能相互通信。
WSS（Web Socket Secure）是WebSocket的加密版本。

http -> new WebSocket('ws://xxx')
https -> new WebSocket('wss://xxx')

}

# tornado提供支持WebSocket的模块是tornado.websocket
{

WebSocketHandler.open()
当一个WebSocket连接建立后被调用。

WebSocketHandler.on_message(message)
当客户端发送消息message过来时被调用，注意此方法必须被重写。

WebSocketHandler.on_close()
当WebSocket连接关闭后被调用。

WebSocketHandler.write_message(message, binary=False)
向客户端发送消息messagea，message可以是字符串或字典（字典会被转为json字符串）。若binary为False，则message以utf8编码发送；二进制模式（binary=True）时，可发送任何字节码。

WebSocketHandler.close()
关闭WebSocket连接。

WebSocketHandler.check_origin(origin)
判断源origin，对于符合条件（返回判断结果为True）的请求源origin允许其连接，否则返回403。可以重写此方法来解决WebSocket的跨域请求（如始终return True）。
}

链接：
https://tornado-zh.readthedocs.io/zh/latest/guide/intro.html
http://demo.pythoner.com/itt2zh/index.html
https://www.jianshu.com/p/3d20a092588d
https://www.zhihu.com/question/50043659/answer/119095429
https://www.zhihu.com/question/50043659/answer/119156752
https://github.com/leporo/tornado-redis/tree/master/demos # 对于不知道怎么异步调用那些异步库的可以参考这里


出现错误  TypeError: initialize() got an unexpected keyword argument 'io_loop'
原因：python环境中，默认tornado版本是最新的5.0，在4.0之后就废弃了io_loop参数。

解决方法：
    1、pip uninstall tornado
    2、pip install tornado==4.1

