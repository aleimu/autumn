# -*- coding:utf-8 -*-
__author__ = "aleimu"
__date__ = "2018.9.28"

# 限制接口短时间调用次数

import redis
import time
from flask import Flask, jsonify, request
from functools import wraps

REDIS_DB = 0
REDIS_HOST = '172.16.4.120'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
IP_LIMIT = 10
TIME_LIMIT = 60

app = Flask(__name__)
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB, socket_timeout=3000)


@app.before_request  # app 装饰器，会对每一个请求都生效
def before_request():
    ip = request.remote_addr
    ip_count = r.get(ip)
    print("ip: %s, ip_count: %s" % (ip, ip_count))
    if not ip_count:
        r.set(ip, 1)
        r.expire(ip, TIME_LIMIT)
    else:
        r.incr(ip)  # 将 key 中储存的数字值增一
        if int(ip_count) > IP_LIMIT:
            return jsonify({'code': 401, 'status': "reach the ip limit", 'message': {}})


# 装饰器 一份钟内限制访问10次，本地缓存
def stat_called_time(func):
    limit_times = [10]  # 这是一个技巧，装饰器内的变量继承每次调用后的变化，变量就必须设置为可变类型
    cache = {}

    @wraps(func)
    def _called_time(*args, **kwargs):
        key = func.__name__
        if key in cache.keys():
            [call_times, updatetime] = cache[key]
            if time.time() - updatetime < TIME_LIMIT:
                cache[key][0] += 1
            else:
                cache[key] = [1, time.time()]
        else:
            call_times = 1
            cache[key] = [call_times, time.time()]
        print('调用次数: %s' % cache[key][0])
        print('限制次数: %s' % limit_times[0])
        if cache[key][0] <= limit_times[0]:
            res = func(*args, **kwargs)
            cache[key][1] = time.time()
            return res
        else:
            print("超过调用次数了")
            return jsonify({'code': 401, 'status': "reach the limit", 'message': {}})

    return _called_time


@app.route("/call")
@stat_called_time
def home():
    return jsonify({'code': 200, 'status': "", 'message': {}})


@app.route("/")
def index():
    return jsonify({'code': 200, 'status': "", 'message': {}})


# 一个小扩展 flask 函数
func_list = []


def a(x):
    print 1, x
    return 1 + x


def b(x):
    print 2, x
    return 2 + x


def c(x):
    print 3, x
    return 3 + x


func_list.append(a)
func_list.append(b)
func_list.append(c)

req = {a: 10}
for fun in func_list:
    req[a] = fun(req[a])
print req[a]

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
