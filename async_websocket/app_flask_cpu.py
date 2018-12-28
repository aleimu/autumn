# -*- coding:utf-8 -*-

'''
服务器cpu监控程序

思路：后端后台线程一旦产生数据，即刻推送至前端。
好处：不需要前端ajax定时查询，节省服务器资源。

'''
import psutil
import time

from threading import Lock

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()


# 后台线程 产生数据，即刻推送至前端
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(5)
        count += 1
        t = time.strftime('%M:%S', time.localtime())  # 获取系统时间（只取分:秒）
        cpus1, cpu2, cpu3, cpu4 = psutil.cpu_percent(interval=None, percpu=True)  # 获取系统cpu使用率 non-blocking
        print(cpus1, cpu2, cpu3, cpu4)
        # print(*cpus)
        # 注意：这里不需要客户端连接的上下文，默认 broadcast = True ！！！！！！！ 启用广播选项
        # socketio.emit('server_response', {'data': [t, *cpus], 'count': count}, namespace='/test')
        socketio.emit('server_response', {'data': [t, cpus1, cpu2, cpu3, cpu4], 'count': count}, namespace='/test',
                      callback=ack)


def ack():
    print ('message was received!')


@app.route('/')
def index():
    return render_template("cpu_index.html", async_mode=socketio.async_mode)


# 与前端建立 socket 连接后，启动后台线程
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8000, debug=True)
