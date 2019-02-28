# -*- coding:utf-8 -*-

import datetime
from flask import Flask, json, jsonify
from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_sqlalchemy import SQLAlchemy, Pagination

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1:3306/camel?charset=utf8'
app.config['SQLALCHEMY_ECHO'] = False


# 方式三
class APIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj.__class__, DeclarativeMeta):
            return self.default({i.name: getattr(obj, i.name) for i in obj.__table__.columns})
        elif isinstance(obj, dict):
            for k in obj:
                try:
                    if isinstance(obj[k], (datetime.datetime, datetime.date, DeclarativeMeta)):
                        obj[k] = self.default(obj[k])
                    else:
                        obj[k] = obj[k]
                except TypeError:
                    obj[k] = None
            return obj
        # elif isinstance(obj, Pagination):
        #     return self.default(obj.items)
        return json.JSONEncoder.default(self, obj)


app.json_encoder = APIEncoder  # 直接修改json对时间格式/SQLAlchemy查询结果的解析方式
db = SQLAlchemy(app)


class ModelMixin(object):
    __slots__ = ()

    def __init__(self, **kwargs):
        pass

    def save(self):
        db.session.add(self)
        self.my_commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            self.my_commit()

    def add(self):
        db.session.add(self)

    def update(self, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                required_commit = True
                setattr(self, k, v)
        if required_commit:
            self.my_commit()
        return required_commit

    def my_commit(self):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def upsert(self, where, **kwargs):
        record = self.query.filter_by(**where).first()
        if record:
            record.update(**kwargs)
        else:
            record = self(**kwargs).save()
        return record

    # 方式二
    def to_json(self):
        if hasattr(self, '__table__'):
            return {i.name: getattr(self, i.name) for i in self.__table__.columns}
        raise AssertionError('<%r> does not have attribute for __table__' % self)


class User(db.Model, ModelMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True)
    fullname = db.Column(db.String(32))
    photo_url = db.Column(db.TEXT)
    fk_location_code = db.Column(db.String(10))
    fk_dept_id = db.Column(db.String(10))
    source = db.Column(db.Integer)
    create_time = db.Column(db.TIMESTAMP, default=datetime.datetime.now())
    update_time = db.Column(db.TIMESTAMP)

    # 方式一
    def to_dict(self):
        dict = {}
        dict.update(self.__dict__)
        if "_sa_instance_state" in dict:
            del dict['_sa_instance_state']
        return dict


@app.route('/1')
def first():
    data = User.query.first()
    print(isinstance(data.__class__, DeclarativeMeta))  # True
    print(isinstance(data, DeclarativeMeta))  # False
    print(isinstance(data.__class__, Query))  # False
    print(isinstance(data, Query))  # False
    print(isinstance(data, User))  # True
    print("-----------------------")
    print(data.__class__)
    print(data.__tablename__)
    print(data.__table__)
    print(dir(data))
    print(data.__dict__)
    print("-----------------------")
    print("to_json:", data.to_json())  # 每种方式都可以单独使用,直接jsonify(data)就行
    print("to_dict:", data.to_dict())
    return jsonify(data)


@app.route('/2')
def list():
    data = User.query.paginate(1, 10, False)
    print(type(data), data)  # Pagination
    print(type(data.items), data.items)  # list
    print("-----------------------")
    print(isinstance(data.__class__, DeclarativeMeta))  # False
    print(isinstance(data, DeclarativeMeta))  # False
    print(isinstance(data.__class__, Query))  # False
    print(isinstance(data, Query))  # False
    print(isinstance(data, Pagination))  # True

    return jsonify(data.items)  # 需要先.items获取结果列表,在放入jsonify中


if __name__ == '__main__':
    app.run(debug=True)
