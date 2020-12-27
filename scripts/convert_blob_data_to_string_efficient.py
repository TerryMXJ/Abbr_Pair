#!/usr/bin/env python
# coding: utf-8
import pymysql
import gevent
import time
import os
import pickle


class MyPyMysql:
    def __init__(self, host, port, username, password, db, charset='utf8'):
        self.host = host  # mysql主机地址
        self.port = port  # mysql端口
        self.username = username  # mysql远程连接用户名
        self.password = password  # mysql远程连接密码
        self.db = db  # mysql使用的数据库名
        self.charset = charset  # mysql使用的字符编码,默认为utf8
        self.data = list()
        self.pymysql_connect()  # __init__初始化之后，执行的函数

    def pymysql_connect(self):
        # pymysql连接mysql数据库
        # 需要的参数host,port,user,password,db,charset
        self.conn = pymysql.connect(host=self.host,
                                    port=self.port,
                                    user=self.username,
                                    password=self.password,
                                    db=self.db,
                                    charset=self.charset
                                    )
        # 连接mysql后执行的函数
        self.build_data()
        # self.asynchronous()
        self.run(nmin=18530001, nmax=18537001)

    def run(self, nmin, nmax):
        # 创建游标
        self.cur = self.conn.cursor()

        # 定义sql语句,插入数据id,name,gender,email
        sql = "insert into page_title_convert(page_id, page_title) values (%s,%s)"
        data = self.data[nmin:nmax]
        # 执行多行插入，executemany(sql语句,数据(需一个元组类型))
        for i in data:
            try:
                self.cur.execute(sql, i)
            except pymysql.err.DataError:
                print('fail insert data: %s' % i[1])
        print('成功插入第{}条数据'.format(nmax - 1))

        # 提交数据,必须提交，不然数据不会保存
        self.conn.commit()

    def asynchronous(self):
        # g_l 任务列表
        # 定义了异步的函数: 这里用到了一个gevent.spawn方法
        max_line = 10000
        g_l = [gevent.spawn(self.run, i, i + max_line) for i in range(1, 18530000, max_line)]

        # gevent.joinall 等待所以操作都执行完毕
        gevent.joinall(g_l)
        self.cur.close()  # 关闭游标
        self.conn.close()  # 关闭pymysql连接

    def build_data(self):
        with open('./output/page_title.pkl', 'rb') as f:
            self.data = pickle.load(f)
        print('file size is %d, load data successfully...' % len(self.data))


if __name__ == '__main__':
    start_time = time.time()  # 计算程序开始时间
    st = MyPyMysql('10.176.34.89', 3306, 'root', '123456', 'wikipedia')  # 实例化类，传入必要参数
    print('程序耗时{:.2f}'.format(time.time() - start_time))  # 计算程序总耗时