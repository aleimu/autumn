# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import hashlib
from flask import Flask, json, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
# SQLALCHEMY_DATABASE_URI = 'mysql://root:root@172.16.4.120:3306/camel?charset=utf8'  # charset=utf8 加上很重要哦
# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_BINDS

SQLALCHEMY_BINDS = {
    'camel': 'mysql://root:root@172.16.4.120:3306/camel?charset=utf8',
    'test': 'mysql://root:root@172.16.4.120:3306/test?charset=utf8'
}
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'SECRET_KEY'
db = SQLAlchemy(app)


class APIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


app.json_encoder = APIEncoder  # 这种方法可以直接修改json对时间格式的解析方式，推荐使用。不用自己再造jsonify_diy轮子


class User(db.Model):
    __bind_key__ = 'camel'
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


class Users(db.Model):
    __bind_key__ = 'test'
    __tablename__ = 'users'
    users_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    names = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(64))
    role = db.Column(db.String(11))

    def __init__(self, names, password, role):
        self.names = names
        self.password = func.md5(password)
        self.role = role

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


@app.route("/1")
def index1():
    id = request.values.get("id")
    username = request.values.get("username")
    info = change_username(id, username)
    return jsonify(info)


def change_username(id, username):
    User.query.filter(User.id == id).update({'username': username + "111"}, synchronize_session=False)
    after_update_info = User.query.filter(User.id == id).first().to_dict()  # 没有提交,但也能查出新的值.......,但数据库没变化
    print "after_update_info:", after_update_info.get("username")
    # db.session.commit()
    change_user_in_different_func(id, username + "222")
    after_update_info = User.query.filter(User.id == id).first().to_dict()  # 没有提交,但也能查出新的值.......,但数据库没变化
    print "after_update_info:", after_update_info.get("username")
    db.session.commit()
    return after_update_info


# 跨多个函数操作,对User的操作也是生效的
def change_user_in_different_func(id, username):
    User.query.filter(User.id == id).update({'username': username}, synchronize_session="evaluate")
    after_update_info = User.query.filter(User.id == id).first().to_dict()
    print "after_update_info:", after_update_info.get("username")


@app.route("/2")
def index2():
    id = request.values.get("id")
    username = request.values.get("username")
    # 'evaluate' 默认值, 会同时修改当前 session 中的对象属性.
    User.query.filter(User.id == id).update({'username': username + "1"}, synchronize_session="evaluate")
    # 'fetch' 修改前, 会先通过 select 查询条目的值.
    User.query.filter(User.id == id).update({'username': username + "2"}, synchronize_session="fetch")
    # 不修改当前 session 中的对象属性.
    User.query.filter(User.id == id).update({'username': username + "3"}, synchronize_session=False)
    return jsonify("true")


@app.route("/3")
def index3():
    id = request.values.get("id")
    username = request.values.get("username")

    User.query.filter(User.id == id).update({'username': username + "1"}, synchronize_session="evaluate")

    db.session.begin_nested()  # savepoint 之前的不会被rollback
    User.query.filter(User.id == id).update({'username': username + "2"}, synchronize_session="fetch")

    User.query.filter(User.id == id).update({'username': username + "3"}, synchronize_session=False)
    db.session.rollback()
    db.session.commit()
    return jsonify("true")


@app.route("/4")
def index4():
    id = request.values.get("id")
    username = request.values.get("username")
    # subtransactions=True 表示允许开启一个子会话 否则会报如下错误:
    # "A transaction is already begun.  Use "InvalidRequestError: A transaction is already begun.  Use subtransactions=True to allow subtransactions.
    db.session.begin(subtransactions=True, nested=True)  # sqlalchemy.orm.session.Session#begin
    User.query.filter(User.id == id).update({'username': username + "1"}, synchronize_session="evaluate")
    db.session.begin_nested()  # savepoint 之前的不会被rollback
    User.query.filter(User.id == id).update({'username': username + "2"}, synchronize_session="fetch")
    db.session.rollback()
    db.session.commit()
    return jsonify("true")


# index4中的操作对应的sql日志

"""
181220 23:04:21	   45 Query	SAVEPOINT sa_savepoint_1
		   45 Query	UPDATE `User` SET username='aaaa1' WHERE `User`.id = '289'
		   45 Query	SAVEPOINT sa_savepoint_2
		   45 Query	SELECT `User`.id AS `User_id` 
FROM `User` 
WHERE `User`.id = '289'
		   45 Query	UPDATE `User` SET username='aaaa2' WHERE `User`.id = '289'
		   45 Query	ROLLBACK TO SAVEPOINT sa_savepoint_2
		   45 Query	RELEASE SAVEPOINT sa_savepoint_1
		   45 Query	rollback
"""


@app.route("/5")
def index5():
    id = request.values.get("id")
    username = request.values.get("username")
    # subtransactions=True 表示允许开启一个子会话 否则会报如下错误:
    # "A transaction is already begun.  Use "InvalidRequestError: A transaction is already begun.  Use subtransactions=True to allow subtransactions.
    db.session.begin(subtransactions=True, nested=True)  # sqlalchemy.orm.session.Session#begin
    User.query.filter(User.id == id).update({'username': username + "1"}, synchronize_session="evaluate")
    User.query.filter(User.id == id).update({'username': username + "2"}, synchronize_session="fetch")
    db.session.commit()
    return jsonify("true")


# index5中的操作对应的sql日志
"""
181220 23:06:58	   46 Query	SAVEPOINT sa_savepoint_1
		   46 Query	UPDATE `User` SET username='aaaa1' WHERE `User`.id = '289'
181220 23:06:59	   46 Query	SELECT `User`.id AS `User_id` 
FROM `User` 
WHERE `User`.id = '289'
		   46 Query	UPDATE `User` SET username='aaaa2' WHERE `User`.id = '289'
		   46 Query	RELEASE SAVEPOINT sa_savepoint_1
		   46 Query	rollback

"""


@app.route("/6")
def index6():
    id = request.values.get("id")
    username = request.values.get("username")
    User.query.filter(User.id == id).update({'username': username + "1"}, synchronize_session="evaluate")
    User.query.filter(User.id == id).update({'username': username + "2"}, synchronize_session="fetch")
    db.session.commit()
    return jsonify("true")


# index6中的操作对应的sql日志
"""
181220 23:21:25	   51 Query	UPDATE `User` SET username='aaaa1' WHERE `User`.id = '289'
		   51 Query	SELECT `User`.id AS `User_id` 
FROM `User` 
WHERE `User`.id = '289'
		   51 Query	UPDATE `User` SET username='aaaa2' WHERE `User`.id = '289'
		   51 Query	commit
181220 23:21:26	   51 Query	rollback
"""


@app.route("/7")
def index7():
    id = request.values.get("id")
    username = request.values.get("username")
    # subtransactions=True 表示允许开启一个子会话 否则会报如下错误:
    # "A transaction is already begun.  Use "InvalidRequestError: A transaction is already begun.  Use subtransactions=True to allow subtransactions.
    child_session = db.session.begin(subtransactions=True)  # sqlalchemy.orm.session.Session#begin
    User.query.filter(User.id == id).update({'username': username + "1"}, synchronize_session="evaluate")
    User.query.filter(User.id == id).update({'username': username + "2"}, synchronize_session="fetch")
    # db.session.commit()
    child_session.commit()  # 子会话必须在父会话前提交修改才能被 父.commit()包含.

    db.session.commit()
    return jsonify("true")


# 未child_session.commit()
"""
		   54 Query	UPDATE `User` SET username='bbbbb1' WHERE `User`.id = '289'
		   54 Query	SELECT `User`.id AS `User_id` 
FROM `User` 
WHERE `User`.id = '289'
		   54 Query	UPDATE `User` SET username='bbbbb2' WHERE `User`.id = '289'
		   54 Query	rollback

"""

# child_session.commit() and db.session.commit()
"""
181220 23:25:19	   55 Query	UPDATE `User` SET username='cccc1' WHERE `User`.id = '289'
		   55 Query	SELECT `User`.id AS `User_id` 
FROM `User` 
WHERE `User`.id = '289'
		   55 Query	UPDATE `User` SET username='cccc2' WHERE `User`.id = '289'
		   55 Query	commit
		   55 Query	rollback
"""


@app.route("/8")
def index8():
    id = request.values.get("id")
    username = request.values.get("username")
    new_users = Users(username, username, username)
    db.session.add(new_users)
    Users.query.filter(Users.users_id == 1).update({'names': username + "1", "password": "aaa", "role": "role"})
    User.query.filter(User.id == id).update({'username': username + "1"})

    db.session.commit()

    return jsonify("true")


# 两个数据库的修改语句
"""
181221  0:03:52	   60 Query	INSERT INTO users (names, password, `role`) VALUES ('cccc', md5('cccc'), 'cccc')
		   60 Query	SHOW WARNINGS
		   60 Query	UPDATE users SET names='cccc1', password='aaa', `role`='role' WHERE users.users_id = 1
		   59 Query	UPDATE `User` SET username='cccc1' WHERE `User`.id = '289'
		   59 Query	commit
		   60 Query	commit
		   59 Query	rollback
		   60 Query	rollback
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, threaded=True, debug=True)
