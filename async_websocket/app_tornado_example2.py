# coding:utf-8

import time
import json
import datetime
import random
import urllib
import tornado
import tornado.httpserver
import tornado.httpclient
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.concurrent import run_on_executor
from tornado import gen
from tornado.options import define, options, parse_command_line
from collections import deque
# 这个并发库在python3自带;在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor
import tornadoredis

define("port", default=8888, type=int)

settings = {"static_path": "template"}


class just_now_router(RequestHandler):
    def get(self):
        self.write("i hope just now see you")


class sleep_long_time_router(RequestHandler):
    def get(self):
        time.sleep(60)
        self.write("sleep 60s")


# 回调方式的异步
class callback_handler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        query = self.get_argument('q')
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch("http://search.twitter.com/search.json?" + \
                     urllib.urlencode({"q": query, "result_type": "recent", "rpp": 100}),
                     callback=self.on_response)

    def on_response(self, response):
        body = json.loads(response.body)
        result_count = len(body['results'])
        now = datetime.datetime.utcnow()
        raw_oldest_tweet_at = body['results'][-1]['created_at']
        oldest_tweet_at = datetime.datetime.strptime(raw_oldest_tweet_at,
                                                     "%a, %d %b %Y %H:%M:%S +0000")
        seconds_diff = time.mktime(now.timetuple()) - \
                       time.mktime(oldest_tweet_at.timetuple())
        tweets_per_second = float(result_count) / seconds_diff
        self.write("""
<div style="text-align: center">
    <div style="font-size: 72px">%s</div>
    <div style="font-size: 144px">%.02f</div>
    <div style="font-size: 24px">tweets per second</div>
</div>""" % (self.get_argument('q'), tweets_per_second))
        self.finish()


# 使用tornado.gen可以达到和使用回调函数的异步请求版本相同的性能
class gen_handler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        query = self.get_argument('q')
        client = tornado.httpclient.AsyncHTTPClient()
        # yield的使用返回程序对Tornado的控制，允许在HTTP请求进行中执行其他任务。
        response = yield tornado.gen.Task(client.fetch,
                                          "http://search.twitter.com/search.json?" + \
                                          urllib.coroutine({"q": query, "result_type": "recent", "rpp": 100}))
        body = json.loads(response.body)
        result_count = len(body['results'])
        now = datetime.datetime.utcnow()
        raw_oldest_tweet_at = body['results'][-1]['created_at']
        oldest_tweet_at = datetime.datetime.strptime(raw_oldest_tweet_at,
                                                     "%a, %d %b %Y %H:%M:%S +0000")
        seconds_diff = time.mktime(now.timetuple()) - \
                       time.mktime(oldest_tweet_at.timetuple())
        tweets_per_second = float(result_count) / seconds_diff
        self.write("""
<div style="text-align: center">
    <div style="font-size: 72px">%s</div>
    <div style="font-size: 144px">%.02f</div>
    <div style="font-size: 24px">tweets per second</div>
</div>""" % (query, tweets_per_second))
        self.finish()


class index_router(RequestHandler):
    def get(self):
        title1 = ''
        try:
            title1 = self.get_argument("text1")
        except:
            self.render("./templates/tailf_index.html", textDiv="")
        if title1:
            self.render("./templates/tailf_index.html", textDiv="textDiv")


class tailf_router(WebSocketHandler):
    executor = ThreadPoolExecutor(10)
    users = set()

    def open(self, *args):
        self.users.add(self)  # 建立连接后添加用户到容器中
        for u in self.users:  # 向已在线用户发送消息
            u.write_message(
                u"[%s]-[%s]-进入聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("WebSocket opened")

    def on_message_nowait(self, message):
        self.write_message("aaa")

    @gen.coroutine
    def on_message_sync(self, message):

        def tail(filename, n=10):
            while True:
                lines = '<br>'.join(list(deque(open(filename), n)))
                print("lines:", lines)
                for u in self.users:
                    self.write_message(lines)
                if lines:
                    gen.sleep(2)
                if "Control-C" in lines:
                    self.close()
                    break

        yield tail('ip.txt')  # 虽然使用了 @gen.coroutine 但是由于内部还是同步阻塞的,所以无法开多个页面查看

    @gen.coroutine
    def on_message(self, message):
        self.client = tornadoredis.Client(host="172.16.4.120")  # 使用了异步redis库
        self.client.connect()
        while True:
            result = yield tornado.gen.Task(self.client.keys, "*")  # 异步
            for u in self.users:
                self.write_message(str(result) + str(random.random()))
                gen.sleep(1)

    def on_close(self):
        self.users.remove(self)  # 用户关闭连接后从容器中移除用户
        for u in self.users:
            u.write_message(
                u"[%s]-[%s]-离开聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("WebSocket closed")


class MessageHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.coroutine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'test_channel')
        self.client.listen(self.on_message)

    def on_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe('test_channel')
            self.client.disconnect()


class redis_example(tornado.web.RequestHandler):
    c = tornadoredis.Client(host="172.16.4.120")
    c.connect()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        result = yield tornado.gen.Task(self.c.keys, '*')
        self.set_header('Content-Type', 'text/html')
        print("result:", result)
        self.write(str(result))
        self.finish(' finish is need,when you use gen!')  # 当使用 gen时返回结果必须使用finish或者render来结束请求并返回数据,之前可以用write
        # self.render("./templates/redis_index.html", result=result)
        # self.finish(str(result))


application = tornado.web.Application([
    (r'/', index_router),
    (r'/text1', index_router),
    (r'/now', just_now_router),
    (r'/ws', tailf_router),
    (r'/track', MessageHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print('Demo is runing at 0.0.0.0:8888\nQuit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()

# 还是那句话:既然选择异步,那就全流程都得异步.
