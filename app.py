from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
# -*- coding=utf8 -*-
# 导入Flask库
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect,url_for
# 导入MySQL库
import pymysql
import re

#导入密码等信息
from HiveSqlInfo import *

app = Flask(__name__)
# 写好的数据库连接函数，
# 传入的是table，数据表的名称
# 返回值是数据表中所有的数据，以元祖的格式返回
def get_Table_Data(table):
    conn = pymysql.connect(
        host=Host, port=3306,
        user='root', passwd=Password,
        db=DataBase, charset='utf8',
    )
    cur = conn.cursor()
    res = cur.execute("select * from " + table)
    res = cur.fetchmany(res)
    cur.close()
    conn.commit()
    conn.close()
    return res

def search_Table_Data(table,ID,column='a'):
    conn = pymysql.connect(
        host='127.0.0.1', port=3306,
        user='root', passwd=Password,
        db=DataBase, charset='utf8',
    )
    cur = conn.cursor()
    #对查询方法进行优化，适配登录时查询使用
    if column == 'a':
        cur.execute("select * from " + table + " where id = 1 or " + column + " = " + str(ID))
    else:
        cur.execute("select * from " + table + " where " + column + " = " + str(ID))
    res = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return res

def delete_Table_Data(table,ID):
    conn = pymysql.connect(
        host='127.0.0.1', port=3306,
        user='root', passwd=Password,
        db=DataBase, charset='utf8',
    )
    conn.query("delete from " + table + " where id  = " + str(ID))
    conn.commit()
    conn.close()
    return

def add_Table_Data(table,ckno,bjno,jsno,startweek,endweek):
    conn = pymysql.connect(
        host='127.0.0.1', port=3306,
        user='root', passwd=Password,
        db=DataBase, charset='utf8',
    )
    conn.query("insert into %s (a,b,c,d,e,f)value(%s,%s,%s,%s,%s,%s)" % (table,ckno,bjno,jsno,startweek,endweek,int(endweek) - int(startweek)))
    conn.commit()
    conn.close()
    return

def update_Table_Data(table,ID,ckno,bjno,jsno,startweek,endweek):
    conn = pymysql.connect(
        host='127.0.0.1', port=3306,
        user='root', passwd=Password,
        db=DataBase, charset='utf8',
    )
    # print(ID,ckno,bjno,jsno,startweek,endweek)
    string1 = "update %s set a=%s, b=%s, c=%s  where id = %s" % (table,ckno,bjno,jsno,str(ID))
    string2 = "update %s set d=%s, e=%s, f=%s  where id = %s" % (table,startweek,endweek,int(endweek) - int(startweek),str(ID))
    print(string1)
    print(string2)
    conn.query(string1)
    conn.query(string2)
    conn.commit()
    conn.close()
    return

#添加登录验证
@app.route('/login', methods=['POST'])
def login_judge():
    account = request.form['username']
    password = request.form['password']
    conn = pymysql.connect(
        host='127.0.0.1', port=3306,
        user='root', passwd=Password,
        db=DataBase, charset='utf8',
    )
    result = search_Table_Data('users',account,column='account')
    user = result[0]
    if str(user[0]) == account and user[1] == password:
        if user[-1] == 1:
            return render_template('teacher_index.html')
        else:
            return render_template('student_index.html')
    else:
        return render_template('login.html')

#查找排课
@app.route('/search', methods=['POST'])
def search():
    # 调用数据库函数，查询数据
    data = search_Table_Data("paike_js",request.form["cxyg"])
    # print(data,len(data))
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        posts.append(dict_data)
    # print posts
    return render_template('teacher.html', posts=posts)

#删除排课
@app.route('/deleteStu',methods=['GET','POST'])
def deleteStu():
    toDeleteWords = request.get_data('toBeDelete')
    toDeleteList = set(re.findall("\d+",bytes.decode(toDeleteWords)))
    print(toDeleteList)
    for ID in toDeleteList:
        print(ID)
        delete_Table_Data('paike_js',ID)

    return redirect(url_for('paike_js'))


#转入新增课程号页面
@app.route('/topkpage',methods=['GET','POST'])
def topkpage():
    return render_template('add_paike.html')

@app.route('/addkecheng',methods=['GET','POST'])
def addkecheng():
    """table,ckno,bjno,jsno,startweek,endweek"""
    add_Table_Data('paike_js',request.form['kcno'],request.form['bjno'],
                   request.form['jsno'],request.form['startweek'],request.form['endweek'])
    return redirect(url_for('paike_js'))

@app.route('/toUDpage/<ID>',methods=['GET','POST'])
def toUDpage(ID):
    data = search_Table_Data("paike_js",ID,column="id")
    dict_data = {}
    dict_data['a'] = data[1][0]
    dict_data['b'] = data[1][1]
    dict_data['c'] = data[1][2]
    dict_data['d'] = data[1][3]
    dict_data['e'] = data[1][4]
    dict_data['f'] = data[1][5]
    print(dict_data)
    return render_template('update_paike.html', posts=dict_data)

@app.route('/updatekecheng',methods=['GET','POST'])
def updatekecheng():
    print(type(request.form['id']),request.form['id'])
    update_Table_Data('paike_js',request.form['id'],request.form['kcno'],request.form['bjno'],request.form['jsno'],request.form['startweek'],request.form['endweek'])
    return redirect(url_for('paike_js'))

# 启动服务器后运行的第一个函数，显示对应的网页内容
@app.route('/', methods=['GET', 'POST'])
def home():
    # return '<a href="/index"><h1 align="center">欢迎使用教务系统---点击进入</h1></a>'
    return render_template('login.html')



# 显示学生首页的函数，可以显示首页里的信息
@app.route('/student_index', methods=['GET'])
def student_index():
    return render_template('student_index.html')

# 显示教师首页的函数，可以显示首页里的信息
@app.route('/teacher_index', methods=['GET'])
def teacher_index():
    return render_template('teacher_index.html')

# 显示教学计划的函数，当有请求发生时，去数据库里查找对应的数据，
# 然后将数据的格式用for循环进行遍历，变成列表的格式，然后返回到页面中，
# 再由页面进行显示数据
@app.route('/jxjh', methods=['GET'])
def jxjh():
    # 调用数据库函数，获取数据
    data = get_Table_Data('jihuaxijie')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        dict_data['g'] = value[6]
        posts.append(dict_data)
    # print posts
    return render_template('teacher.html', posts=posts)


# 显示管理班的函数页面
@app.route('/guanliban', methods=['GET'])
def guanliban():
    # 调用数据库函数，获取数据
    data = get_Table_Data('guanliban')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        posts.append(dict_data)
    # print posts
    return render_template('teacher.html', posts=posts)

# 显示排课信息的函数页面
@app.route('/paike_js', methods=['GET'])
def paike_js():
    # 调用数据库函数，获取数据
    data = get_Table_Data('paike_js')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        posts.append(dict_data)
    print(posts[0])
    return render_template('teacher.html', posts=posts)

# 显示学生成绩的页面，包括调用学生成绩数据表
@app.route('/xscj', methods=['GET'])
def xscj():
    # 调用数据库函数，获取数据
    data = get_Table_Data('xueshengchengji')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        posts.append(dict_data)
    # print posts
    return render_template('teacher.html', posts=posts)

# 显示学生类别的页面，包括调用学生成绩数据表
@app.route('/xslb', methods=['GET'])
def xslb():
    # 调用数据库函数，获取数据
    data = get_Table_Data('xslb')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        posts.append(dict_data)
    # print posts
    return render_template('teacher.html', posts=posts)


# 显示田楼教室的函数页面
@app.route('/tjiaoshi', methods=['GET'])
def tjiaoshi():
    # 调用数据库函数，获取数据
    data = get_Table_Data('tjiaoshi')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        posts.append(dict_data)
    # print posts
    return render_template('student.html', posts=posts)

# 显示课程的函数页面
@app.route('/kecheng', methods=['GET'])
def kecheng():
    # 调用数据库函数，获取数据
    data = get_Table_Data('kecheng')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        posts.append(dict_data)
    # print posts
    return render_template('student.html', posts=posts)

# 显示专业的函数页面
@app.route('/zhuanye', methods=['GET'])
def zhuanye():
    # 调用数据库函数，获取数据
    data = get_Table_Data('zhuanye')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        posts.append(dict_data)
    # print posts
    return render_template('student.html', posts=posts)

# 显示学院的函数页面
@app.route('/xueyuan', methods=['GET'])
def xueyuan():
    # 调用数据库函数，获取数据
    data = get_Table_Data('xueyuan')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        posts.append(dict_data)
    # print posts
    return render_template('student.html', posts=posts)

# 显示教师信息的页面，
@app.route('/js', methods=['GET'])
def js():
    # 调用数据库函数，获取数据
    data = get_Table_Data('jiaoshi')
    # 用列表的格式存放全部数据
    posts = []
    for value in data:
        dict_data = {}
        dict_data['a'] = value[0]
        dict_data['b'] = value[1]
        dict_data['c'] = value[2]
        dict_data['d'] = value[3]
        dict_data['e'] = value[4]
        dict_data['f'] = value[5]
        dict_data['g'] = value[6]
        dict_data['h'] = value[7]
        dict_data['i'] = value[8]
        dict_data['j'] = value[9]
        posts.append(dict_data)
    # print posts
    return render_template('xscj.html', posts=posts)


# 主函数
if __name__ == '__main__':
    # app.debug = True
    app.run()