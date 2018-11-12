# -*- coding: utf-8 -*-
"""
tiny_example.py
:copyright: (c) 2015 by C. W.
:license: GPL v3 or BSD
"""
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import traceback
from flask import Flask, request, jsonify, redirect, url_for
import flask_excel as excel
from flask_sqlalchemy import SQLAlchemy  # sql operations


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # jsonify返回的json串支持中文显示
SQLALCHEMY_DATABASE_URI = 'mysql://root:root@172.16.4.120:3306/execl?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
excel.init_excel(app)


@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print('upload_file request data: %s' % (request.values.items()))
        # print("read_sheet_by_index:", request.BookReader(file_name='file'))
        # print("get_sheet:", request.get_sheet(field_name='file'))
        # print("get_book:", request.get_book(field_name='file'))
        # print("get_book_dict:", request.get_book_dict(field_name='file'))
        # all_list = request.get_array(field_name='file')
        # print("get_array:", list_roads)
        # print("get_dict:", request.get_dict(field_name='file'))
        # print("get_dict:", request.get_array(field_name='file', sheet_name="category"))
        # print("get_dict:", request.get_dict(field_name='file', sheet_name="post"))
        # print("list_code:", list_code)

        list_codes = request.get_array(field_name='file', sheet_name="Sheet2")
        list_roads = request.get_array(field_name='file', sheet_name="Sheet1")
        error = upload_execl_roads(list_codes, list_roads)
        print("view error:", error)
        if error:
            return jsonify({"result": error})
        else:
            return jsonify({"result": 'import success'})
        # return jsonify({"result": request.get_array(field_name='file', sheet_name="post")})
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (csv, tsv, csvz, tsvz only)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''


# 上传前execl做去重，execl中的重复内容作为更新数据库记录
def upload_execl_roads(list_codes, list_roads):
    # print("list_codes:", list_codes)
    # print("list_roads:", list_roads)
    # row, column
    try:
        # print(isinstance(list_codes[0][1], unicode), type(list_codes[0][1]))
        # print(isinstance(list_codes[1][1], int), type(list_codes[1][1]))
        # [u '浙江省湖州市', 572001]
        if isinstance(list_codes[0][1], unicode):  # 删除表头
            list_codes.pop(0)
        # get tl_name_by code # todo
        list_codes = dict(list_codes)
    except Exception as e:
        print("error:", traceback.format_exc(), e)
        return str(e)
    will_to_commit = []
    try:
        check_duplicate = set()
        unfind_code = []
        row_index = len(list_roads)
        # print(isinstance(list_roads[0][2], unicode), type(list_roads[0][2]))
        # print(isinstance(list_roads[0][3], unicode), type(list_roads[0][3]))
        # print(isinstance(list_roads[1][3], float), type(list_roads[1][3]))
        # [u '安徽省安庆市-杭州转运中心', 66.92, 435, 390.01793185893604]
        if isinstance(list_roads[0][2], unicode) and isinstance(list_roads[0][3], unicode):  # 删除表头
            list_roads.pop(0)
        for i, road in enumerate(reversed(list_roads)):
            # execl重复项以后一条为准
            if road[0] not in check_duplicate:
                check_duplicate.add(road[0])
                try:
                    start_name, end_name = road[0].split('-')
                except Exception as error1:
                    raise Exception("检查Sheet1 第 %s 行 , %s 格式有错误!" % (row_index - i, road[0]))
                    # raise Exception("check row %s , %s format error in Sheet1!" % (row_index - i, road[0]))
                if not (start_name and end_name):
                    raise Exception("检查Sheet1 第 %s 行 , %s 格式有错误!" % (row_index - i, road[0]))
                    # raise Exception("check row %s , %s format error in Sheet1!" % (row_index - i, road[0]))
                full_take_time = round(road[3])
                full_distance = round(road[2])
                start_code = list_codes.get(start_name)
                if not start_code:
                    unfind_code.append(start_name)
                    continue
                    # raise Exception("在Sheet2 中没有找到 %s 对应的编码!" % start_name)
                    # raise Exception("not find %s code in Sheet2!" % start_name)
                end_code = list_codes.get(end_name)
                if not end_code:
                    unfind_code.append(end_name)
                    continue
                    # raise Exception("在Sheet2 中没有找到 %s 对应的编码!" % end_name)
                    # raise Exception("not find %s code in Sheet2." % end_name)
                # db.session.flush()
                one_road = db.session.query(Road_section).filter(
                    Road_section.road_name == start_name + "-" + end_name).first()  # check_road_duplicate
                if one_road:
                    one_road.full_take_time = full_take_time
                    one_road.full_distance = full_distance
                    one_road.update_time = datetime.datetime.now()
                else:
                    one_road = Road_section(start_org_code=start_code, start_org_name=start_name, end_org_code=end_code,
                                            end_org_name=end_name,
                                            full_take_time=full_take_time, full_distance=full_distance)
                will_to_commit.append(one_road)
        # print("will_to_commit:", will_to_commit)
        if unfind_code:
            unfind_code_str = ','.join(unfind_code)
            raise Exception("在Sheet2 中没有找到 %s 对应的编码!" % unfind_code_str)
        db.session.add_all(will_to_commit)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        print("error:", traceback.format_exc(), error)
        return str(error)


class Road_section(db.Model):
    __tablename__ = 'Road_section'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    road_name = db.Column('road_name', db.String(100), unique=True, nullable=False)  # 路段名称
    start_org_code = db.Column('start_org_code', db.String(10))  # 起始点编号
    start_org_name = db.Column('start_org_name', db.String(50))  # 起始点名称
    end_org_code = db.Column('end_org_code', db.String(10))
    end_org_name = db.Column('end_org_name', db.String(50))
    status = db.Column('status', db.Integer)  # 线路使用状态(0：可使用；1：禁用)
    full_take_time = db.Column('full_take_time', db.Integer)  # 总耗时分钟
    full_distance = db.Column('full_distance', db.Integer)  # 总里程千米
    reason = db.Column('reason', db.String(100))  # 禁用理由
    create_time = db.Column('create_time', db.TIMESTAMP, default=datetime.datetime.now())
    update_time = db.Column(db.TIMESTAMP)

    def __init__(self, start_org_code, start_org_name, end_org_code, end_org_name, full_take_time, full_distance):
        self.road_name = start_org_name + "-" + end_org_name
        self.start_org_code = start_org_code
        self.start_org_name = start_org_name
        self.end_org_code = end_org_code
        self.end_org_name = end_org_name
        self.status = 0
        self.full_take_time = full_take_time
        self.full_distance = full_distance
        self.create_time = datetime.datetime.now()


@app.route("/download", methods=['GET'])
def download_file():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")


test_list = [['名字', '分数'], [1, 2], [3, 4], [5.0, 6.1], ["A", "B"], ['名字1', '分数2'], [1, 2], [3, 4], [5.0, 6.1],
             ["A", "B"]]

# test_list = [['name', 'code'], [1, 2], [3, 4], [5.0, 6.1], ["A", "B"], ['name1', 'code1'], [1, 2], [3, 4], [5.0, 6.1],["A", "B"]]


@app.route("/export", methods=['GET'])
def export_records():
    return excel.make_response_from_array(test_list, "csv", file_name="export_data")


@app.route("/download_file_named_in_unicode_csv", methods=['GET'])
def download_file_named_in_unicode():
    return excel.make_response_from_array(test_list, "csv", file_name=u"中文文件名", encoding="ansi")
# fixme 导出csv格式后内容出现中文乱码，分数和名字都是ANSI格式的，需要解决

@app.route("/download_file_named_in_unicode_xls", methods=['GET'])
def download_file_named_in_unicode_xls():
    return excel.make_response_from_array(test_list, "xls", file_name=u"xls中文文件名")
# fixme 有异常  UnicodeDecodeError: 'ascii' codec can't decode

@app.route("/download_file_named_in_unicode_xlsx", methods=['GET'])
def download_file_named_in_unicode_xlsx():
    return excel.make_response_from_array(test_list, "xlsx", file_name=u"xlsx中文文件名")


"""

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                               backref=db.backref('posts',
                                                  lazy='dynamic'))

    def __init__(self, title, body, category, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.category = category

    def __repr__(self):
        return '<Post %r>' % self.title


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


# db.create_all()
@app.route("/import", methods=['GET', 'POST'])
def doimport():
    if request.method == 'POST':
        def category_init_func(row):
            print("row['name']:", row['name'])
            c = Category(row['name'])
            c.id = row['id']
            return c

        def post_init_func(row):
            # print("row['name']:", row['name'])
            print("row['category']:", row['category'])
            c = Category.query.filter_by(name=row['category']).first()
            p = Post(row['title'], row['body'], c, row['pub_date'])
            return p

        try:
            request.save_book_to_database(
                field_name='file', session=db.session,
                tables=[Category, Post],
                initializers=[category_init_func, post_init_func])
        except Exception as e:
            return jsonify({"result": str(e)})
        return jsonify({"result": "ok"})
        # return redirect(url_for('.handson_table'), code=302)
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''


@app.route("/export", methods=['GET'])
def doexport():
    return excel.make_response_from_tables(db.session, [Category, Post], "xls")


@app.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(
        db.session, [Category, Post], 'handsontable.html')


@app.route("/custom_export", methods=['GET'])
def docustomexport():
    query_sets = Category.query.filter_by(id=1).all()
    column_names = ['id', 'name']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls")
"""

# insert database related code here
if __name__ == "__main__":
    app.run(port=6000)
