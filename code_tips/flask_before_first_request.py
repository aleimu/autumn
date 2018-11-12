# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import hashlib
from flask import Flask, json, Response, jsonify, render_template, render_template_string
from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_DATABASE_URI = 'mysql://root:root@172.16.4.120:3306/camel?charset=utf8'  # charset=utf8 加上很重要哦
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY'
db = SQLAlchemy(app)


def jsonify_diy(data):
    # flask default jsonify function not surport datetime serialize
    return Response(json.dumps(data, cls=APIEncoder), mimetype='application/json')


class APIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        # if isinstance(obj, datetime):
        #     return http_date(obj.utctimetuple())
        # if isinstance(obj, date):
        #     return http_date(obj.timetuple())
        return json.JSONEncoder.default(self, obj)


app.json_encoder = APIEncoder  # 这种方法可以直接修改json对时间格式的解析方式，推荐使用。不用自己再造jsonify_diy轮子


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column('hash', db.String(256), nullable=False)
    email = db.Column('email', db.String(64))
    mobile = db.Column('mobile', db.String(11))
    telephone = db.Column('telephone', db.String(11))
    type = db.Column('role_type', db.Integer, nullable=False)
    active = db.Column('active', db.Integer, default=0)
    username = db.Column('username', db.String(32), index=True, unique=True)
    photo_url = db.Column('photo_url', db.TEXT)
    user_no = db.Column('user_no', db.String(32), index=True, unique=True)
    fk_dept_id = db.Column(db.Integer)
    create_time = db.Column('create_time', db.TIMESTAMP, default=datetime.datetime.now())
    update_time = db.Column('update_time', db.TIMESTAMP)
    user_type = db.Column('user_type', db.Integer, default=2)

    def __init__(self, username, password, email, mobile, telephone, role_type, fullname,
                 photo_url, active, user_no, registration_id, fk_location_code, user_type):
        self.username = username
        m2 = hashlib.md5()
        m2.update(password)
        self.hash = m2.hexdigest()
        self.email = email
        self.mobile = mobile
        self.telephone = telephone
        self.role_type = role_type
        self.fullname = fullname
        self.photo_url = photo_url
        self.active = active
        self.create_time = datetime.datetime.now()
        self.zh_name = fullname
        self.user_no = user_no
        self.registration_id = registration_id
        self.fk_location_code = fk_location_code
        self.user_type = user_type

    def to_dict(self):
        dict = {}
        dict.update(self.__dict__)
        if "_sa_instance_state" in dict:
            del dict['_sa_instance_state']
        return dict


@app.before_first_request
def before_first_request_func_1():
    print("before_first_request")


@app.before_request
def before_request_fun_1():
    print("before_request")


@app.after_request
def after_request(response):
    print("after_request")
    response.headers['Content-Type'] = 'text/html'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = "Referer, Accept, Origin, User-Agent"
    return response


@app.teardown_request
def teardown_request(response):
    print("teardown_request")


@app.route("/")
def https_index():
    html_str = u'''
        <!DOCTYPE html>
    <html>
    <head> 
    <meta charset="utf-8"> 
    <!--meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"-->
    <title>测试</title> 
    <script src="https://libs.baidu.com/jquery/1.10.2/jquery.min.js">
    </script>
    <script>
    $(document).ready(function(){
    	$("#button1").click(function(){
    		$.get("https://127.0.0.1:6000/get",function(data,status){
    			alert("数据: " + data + "状态: " + status);
    		});
    	});
    });
    $(document).ready(function(){
    	$("#button2").click(function(){
    		$.get("https://appdrivert1.yoohoor.com:5009/users/char?token=aeae3596-e63d-11e8-86d3-00163e050akk&page_index=1&retrieve_username=&retrieve_fullname=&retrieve_delete=&role_type=0&page_size=10",function(data,status){
    			alert("数据: " + data + "状态: " + status);
    		});
    	});
    });

    $(document).ready(function(){
    	$("#button3").click(function(){
    		$.get("http://127.0.0.1:8000/index0",function(data,status){
    			alert("数据: " + data + "状态: " + status);
    		});
    	});
    });

    </script>
    </head>
    <body>

    <button id="button1">请求本服务的 HTTPS 接口</button></br>
    <button id="button2">跨域请求其他服务的 HTTPS 接口</button></br>
    <button id="button3">跨域请求其他服务的 HTTP 接口</button>
    </body>
    </html>

        '''
    return render_template_string(html_str)


@app.route("/get")
def https_index_test():
    return jsonify([1, 2, 3, 4, 5])


dome_respones1 = {"code": 200, "date": [1, 2, 3, 4, 5], "time": datetime.datetime.now()}


@app.route("/1")
def index1():
    return jsonify(dome_respones1)


'''
{
  "code": 200,
  "date": [
    1,
    2,
    3,
    4,
    5
  ],
  "time": "Thu, 01 Nov 2018 14:29:42 GMT"
}
'''


@app.route("/2")
def index2():
    one_user = db.session.query(User).first()
    return jsonify(one_user.to_dict())


"""
# curl "http://127.0.0.1:6000/2"
{
  "active": 1,
  "create_time": "Wed, 11 May 2016 12:47:03 GMT",
  "delete_flag": 1,
  "email": "",
  "fk_dept_id": null,
  "fk_location_code": "000001",
  "fullname": "\u4e1c\u534e\u8c03\u5ea6\u5468",
  "hash": "f642e86b7589043b343e5e8ba514ca01",
  "id": 289,
  "mobile": "",
  "photo_url": "./upload/IMG_20170321_152440_s__s_.jpg",
  "registration_id": "",
  "role_type": 1,
  "telephone": "021-69773577",
  "update_time": "Thu, 17 Aug 2017 10:39:28 GMT",
  "user_no": "00000001",
  "user_type": 2,
  "username": "00000001",
  "zh_name": "\u4e1c\u534e\u8c03\u5ea6\u5468"
}
"""


@app.route("/3")
def index3():
    return jsonify_diy(dome_respones1)


# {"code": 200, "date": [1, 2, 3, 4, 5], "time": "2018-11-01 14:29:00"}

@app.route("/4")
def index4():
    one_user = db.session.query(User).first()
    return jsonify_diy(one_user.to_dict())


"""
# curl "http://127.0.0.1:6000/4"
{"active": 1, "create_time": "2016-05-11 12:47:03", "delete_flag": 1, "email": "", "fk_dept_id": null, 
"fk_location_code": "000001", "fullname": "\u4e1c\u534e\u8c03\u5ea6\u5468", 
"hash": "f642e86b7589043b343e5e8ba514ca01", "id": 289, "mobile": "", 
"photo_url": "./upload/IMG_20170321_152440_s__s_.jpg", "registration_id": "",
 "role_type": 1, "telephone": "021-69773577", "update_time": "2017-08-17 10:39:28",
  "user_no": "00000001", "user_type": 2, "username": "00000001", 
  "zh_name": "\u4e1c\u534e\u8c03\u5ea6\u5468"}
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, threaded=True, debug=True, ssl_context='adhoc')  # ssl_context 启用https
    # 其中的https_index 、https_index_test是为了验证https网页内请求http和https，跨域情况,其他接口是为了看看jsonify对时间的解析情况
