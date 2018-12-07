# -*- coding:utf-8 -*-
__author__ = "aleimu"
__date__ = "2018-12-6"
__doc__ = "一个实用的入参校验装饰器--针对目前,前端 url?&a=1&b=2或-d'a=1&b=2c=qwe'形式的非json(所有参数都是str类型)" \
          "入参的校验"

import copy
import traceback
from collections import OrderedDict
from functools import wraps
from flask import Flask, json, jsonify, request

app = Flask(__name__)


def verify_args(need=None, length=None, check=None, strip=True, default=(False, None), diy_func=None, release=False):
    """
    约束:
    1. 简化了传参校验,使用位置传参或者关键词传参(一个参数对应一个参数),不允许使用one to list等python高级传参特性
    2. 所有的参数都是str/unicode类型的,前端没有使用json带参数类型的入参方式
    :param need: 必须参数,且不能为None或者""
    :param length: 参数长度范围
    :param check:  str的常用类方法/属性如下:
        isalnum 判断字符串中只能由字母和数字的组合，不能有特殊符号
        isalpha 字符串里面都是字母，并且至少是一个字母，结果就为真，（汉字也可以）其他情况为假
        isdigit 函数判断是否全为数字
    :param strip:对字段进行前后过滤空格
    :param default:将"" 装换成None
    :param diy_func:自定义的对某一参数的校验函数格式: {key:func},类似check
    :param release:发生参数校验异常后是否依然让参数进入主流程函数
    :return:
    """

    def wraps_1(f):
        @wraps(f)
        def wraps_2(*args, **kwargs):
            if release:
                args_bak = args[:]
                kwargs_bak = copy.deepcopy(kwargs)  # 下面流程异常时,是否直接使用 原参数传入f todo
            print ("in", args, kwargs)
            args_template = f.func_code.co_varnames
            print("args_template:", args_template)
            args_dict = OrderedDict()
            req_args_need_list = []
            req_args_types_list = []
            try:
                for i, x in enumerate(args):
                    args_dict[args_template[i]] = x
                sorted_kwargs = sort_by_co_varnames(args_template, kwargs)
                args_dict.update(sorted_kwargs)
                print("args_dict:", args_dict)
                # need
                if need:
                    for k in need:
                        if k not in args_dict:
                            req_args_need_list.append(k)
                        else:
                            if args_dict[k] == None or args_dict[k] == "":
                                req_args_need_list.append(k)
                    if req_args_need_list:
                        return False, "%s is in need" % req_args_need_list
                # strip
                if strip:
                    for k in args_dict:
                        if args_dict[k]:
                            args_dict[k] = args_dict[k].strip()
                # length
                if length:
                    for k in args_dict:
                        if k in length:
                            if not (len(args_dict[k]) >= length[k][0] and len(args_dict[k]) <= length[k][1]):
                                return False, "%s length err" % k
                # default:
                if default[0]:
                    for x in args_dict:
                        if args_dict[x] == "":
                            args_dict[x] = default[1]
                # check
                if check:
                    for k in check:
                        check_func = getattr(type(args_dict[k]), check[k], None)
                        if not (k in args_dict and check_func and check_func(args_dict[k])):
                            req_args_types_list.append(k)
                    if req_args_types_list:
                        return False, "%s type err" % req_args_types_list
                # diy_func
                if diy_func:
                    for k in args_dict:
                        if k in diy_func:
                            args_dict[k] = diy_func[k](args_dict[k])
            except Exception as e:
                print("verify_args catch err: ", traceback.format_exc())
                if release:
                    return f(*args_bak, **kwargs_bak)
                else:
                    return False, str(e)
            return f(*args_dict.values())

        return wraps_2

    return wraps_1


def sort_by_co_varnames(all_args, kwargs):
    new_ordered = OrderedDict()
    for x in all_args:
        if x in kwargs:
            new_ordered[x] = kwargs[x]
    return new_ordered


@app.route("/", methods=["GET", "POST", "PUT"])
def index():
    a = request.values.get("a")
    b = request.values.get("b")
    c = request.values.get("c")
    d = request.values.get("d")
    e = request.values.get("e")
    f = request.values.get("f")
    g = request.values.get("g")
    status, data = todo(a, b, c, d, e=e, f=f, g=g)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


@verify_args(need=['a', 'b', 'c'], length={"a": (6, 50)}, strip=True,
             check={"b": 'isdigit', "c": "isalnum"},
             default=(True, None),
             diy_func={"a": lambda x: x + "aa"})
def todo(a, b, c, d, e='  1  ', f='2    ', g=''):
    return True, {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, debug=True)


"""
# curl "http://127.0.0.1:6000/" -d "pwd=123&a=1111111&b=2&c=3&d=d&e=eeeeee&f=12345&g="
{
  "code": 200,
  "data": {
    "a": "1111111aa",
    "b": "2",
    "c": "3",
    "d": "d",
    "e": "eeeeee",
    "f": "12345",
    "g": null
  },
  "err": null
}

# curl "http://127.0.0.1:6000/" -d "pwd=123&a=1111111&b=2&c=3346()*&d=d&e=eeeeee&f=12345&g="
{
  "code": 500,
  "data": null,
  "err": "['c'] type err"
}

# curl "http://127.0.0.1:6000/" -d "pwd=123&a=1111111&b=2&c=&d=d&e=eeeeee&f=12345&g="    
{                                                                                        
  "code": 500,                                                                           
  "data": null,                                                                          
  "err": "['c'] is in need"                                                              
}   

# curl "http://127.0.0.1:6000/" -d "pwd=123&a=1111111&b=2&c=  1  &d=d&e=eeeeee&f=12345&g="  
{                                                                                           
  "code": 200,                                                                              
  "data": {                                                                                 
    "a": "1111111aa",                                                                       
    "b": "2",                                                                               
    "c": "1",                                                                               
    "d": "d",                                                                               
    "e": "eeeeee",                                                                          
    "f": "12345",                                                                           
    "g": null                                                                               
  },                                                                                        
  "err": null                                                                               
}                                                                                                                                                                                
"""