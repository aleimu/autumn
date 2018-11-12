# -*- coding:utf-8 -*-

import json
from flask import Flask, jsonify, request
from flask_limiter import Limiter, HEADERS  # https://github.com/alisaifee/flask-limiter
from flask_limiter.util import get_remote_address

# import limits.storage   # https://github.com/alisaifee/limits/tree/master/limits    依赖了这个limits库

RATELIMIT_STORAGE_URL = "redis://172.16.4.120:6379"  # 将被限制不可以再正常访问的请求放入缓存
app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'text/html'  # 避免ie8把json数据以下载方式打开
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = "Referer, Accept, Origin, User-Agent"
    return response


limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=RATELIMIT_STORAGE_URL,
    headers_enabled=True  # X-RateLimit写入响应头。
)
"""
root@(none):~# curl -v "http://172.16.2.197:6000/index4"
* Hostname was NOT found in DNS cache
*   Trying 172.16.2.197...
* Connected to 172.16.2.197 (172.16.2.197) port 6000 (#0)
> GET /index4 HTTP/1.1
> User-Agent: curl/7.35.0
> Host: 172.16.2.197:6000
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: text/html
< X-RateLimit-Limit: 2
< X-RateLimit-Remaining: 1
< X-RateLimit-Reset: 1539849353
# X-RateLimit-Limit	活动窗口允许的请求总数
# X-RateLimit-Remaining	活动窗口中剩余的请求数。
# X-RateLimit-Reset	自重建窗口以来的UTC时间以来的UTC秒数。
< Retry-After: 3600
< Content-Length: 32
< Server: Werkzeug/0.14.1 Python/2.7.9
< Date: Thu, 18 Oct 2018 06:55:52 GMT
< 
{
  "response": "mysql_limit"
}
"""


@app.route("/slow")
@limiter.limit("1 per day")
def slow():
    return "24"


# curl -v "http://172.16.2.197:6000/slow"
# 127.0.0.1:6379> keys *
# 1) "LIMITER/172.16.4.120/slow/1/1/day"
# 127.0.0.1:6379> TTL "LIMITER/172.16.4.120/slow/1/1/day"
# (integer) 86285       # 设定的失效时间是 1 天

@app.route("/fast")  # 默认访问速率
def fast():
    return "42"


@app.route("/ping")
@limiter.exempt  # 无访问速率限制
def ping():
    return "PONG"


@app.route("/")
@limiter.limit("1/second", error_message='chill!')
@limiter.limit("100/day")
@limiter.limit("10/hour")
@limiter.limit("1/minute")
def index():
    return "index"


# curl -v "http://172.16.2.197:6000/" # 访问了一次就触发了下面三条redis记录，清理掉redis记录，可以一分钟内再次访问
# 127.0.0.1:6379> keys *
# 2) "LIMITER/172.16.4.120/index/10/1/hour"
# 3) "LIMITER/172.16.4.120/index/100/1/day"
# 4) "LIMITER/172.16.4.120/index/1/1/minute"


@app.route('/index0')
@limiter.limit("100/30seconds", error_message=json.dumps({"data": "You hit the rate limit", "error": 429}))
def index0():
    return jsonify({'response': 'This is a rate limited response'})


@app.route('/index2')
@limiter.limit("100/day;10/hour;1/minute")  # 与index()同功效
def index2():
    return jsonify({'response': 'Are we rated limited?'})


@app.route('/index3')
@limiter.exempt
def index3():
    return jsonify({'response': 'We are not rate limited'})


@app.route("/expensive")  # exempt_when=callable 当满足给定条件时，可以免除限制
@limiter.limit("1/day", exempt_when=lambda: get_remote_address() == "172.16.4.120")
def expensive_route():
    return jsonify({'response': 'you are wellcome!'})


# 多个路由应共享速率限制的情况（例如，访问有限速率的相同资源保护路由时）
mysql_limit = limiter.shared_limit("2/hour", scope="mysql_flag")
# 3) "LIMITER/172.16.4.120/mysql_flag/2/1/hour"

@app.route('/index4')
@mysql_limit
def index4():
    return jsonify({'response': 'mysql_limit'})


@app.route('/index5')
@mysql_limit
def index5():
    return jsonify({'response': 'mysql_limit'})


def host_scope(endpoint_name):
    return request.host

# 动态共享限制
host_limit = limiter.shared_limit("2/hour", scope=host_scope)
# 1) "LIMITER/172.16.4.120/172.16.2.197:6000/2/1/hour"

@app.route('/index6')
@host_limit
def index6():
    return jsonify({'response': 'host_limit'})


@app.route('/index7')
@host_limit
def index7():
    return jsonify({'response': 'host_limit'})


# @limiter.request_filter这个装饰器只是将一个函数标记为将要测试速率限制的请求的过滤器。如果任何请求过滤器返回True，
# 则不会对该请求执行速率限制。此机制可用于创建自定义白名单。

@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == "127.0.0.1"


@limiter.request_filter
def header_whitelist():
    return request.headers.get("X-Internal", "") == "true"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, threaded=True)
