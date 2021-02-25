# -*- coding:utf-8 -*-
__doc__ = "动态转发,可配置规则"

from flask import request, jsonify, Flask
import requests

app = Flask(__name__)

url_dict = {
    "server1": "http://127.0.0.1:85/",
    "server2": "http://127.0.0.1:5000/",
    "server3": 'http://127.0.0.1:82/',
    "server4": 'http://127.0.0.1:5003/',
    "server5": 'http://127.0.0.1:5002/',
}


# 动态转发1
@app.errorhandler(404)
def not_found(error):
    if request.values.get("projectCode"):
        url = url_dict.get(request.values.get("projectCode")) + request.path
        result = requests.request(request.method, url, data=request.values.to_dict(), json=request.json,
                                  headers=request.headers, timeout=1)
        print(result.text)
        if result.status_code == 200:
            return result.json()
        else:
            return jsonify({"code": result.status_code, "msg": "转发失败"})
    return jsonify({"code": 1500, "msg": "not find"})


# 动态转发2
@app.route("/transfer/<path:path>", methods=["POST", "PUT", "GET", "DELETE", "OPTIONS", "PATCH", "HEAD"])
def transfer(path):
    url = url_dict.get(request.values.get("projectCode")) + path
    result = requests.request(request.method, url, data=request.values.to_dict(), json=request.json,
                              headers=request.headers, timeout=1)
    print(result.text)
    if result.status_code == 200:
        return result.json()
    else:
        return jsonify({"code": result.status_code, "msg": "转发失败"})


if __name__ == '__main__':
    app.run()
