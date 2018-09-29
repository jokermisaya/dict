'''
name: Tedu
date: 2018-09-28
phone:XXX
modules:pymsql...
This is a dict for AID
'''
from socket import *
import os
import sys
import time
import pymysql
import signal

#定义需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)

#流程控制
def main():
    #创建数据库连接
    db = pymysql.connect('localhost','root','123456','dict')
    
    #创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    #忽略子进程信号
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue

        #创建子进程
        pid = os.fork()
        if pid == 0:
            s.close()
            print('子进程准备就绪')
            do_child(c,db)
        else:
            c.close()
            continue
 
def do_child(c,db):
    while True:
        data = c.recv(128).decode()
        print(c.getpeername(),":",data)
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c,db,data)
        elif data[0] == 'L':
            do_login(c,db,data)
        elif data[0] == 'Q':
            do_query(c,db,data)
        elif data[0] == 'H':
            do_hist(c,db,data)

def do_register(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]

    cursor = db.cursor()
    sql = "select * from user where name = '%s'"%name
    cursor.execute(sql)
    r = cursor.fetchone()
    #用户存在反馈给客户端
    if r != None:
        c.send(b'EXISTS')
        return
    #用户不存在插入用户
    sql = "insert into user (name,passwd) values('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FALL')
        return
    else:
        print('%s注册成功'%name)

def do_login(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql = "select * from user where name = '%s' and passwd = '%s'"%(name,passwd)
    cursor.execute(sql)
    r = cursor.fetchone()
    if r == None:
        c.send(b'FALL')
    else:
        print('%s登录成功'%name)
        c.send(b'OK')


def do_query(c,db,data):
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()

    def insert_history():
        tm = time.ctime()
        sql = "insert into hist (name,word,time) values ('%s','%s','%s')"%(name,word,tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            return
    #文本查询
    try:
        f = open(DICT_TEXT,'rb')
    except:
        c.send('服务器异常'.encode())
        return
    while True:
        line = f.readline().decode()
        w = line.split(' ')[0]
        if (not line) or w > word:
            c.send('没有找到该单词'.encode())
            break
        elif w == word:
            c.send(b'OK')
            time.sleep(0.1)
            c.send(line.encode())
            insert_history()
            break
    f.close()

def do_hist(c,db,data):
    name = data.split(' ')[1]
    cursor = db.cursor()

    try:
        sql = "select * from hist where name = '%s'"%name
        cursor.execute(sql)
        r = cursor.fetchall()
        if not r:
            c.send('没有历史记录'.encode())
            return
        else:
            c.send(b'OK')
    except:
        c.send('数据库查询出错'.encode())
        return
    #n = 0
    for i in r:
        n += 1
        if n>10:
            break
        time.sleep(0.1)
        msg = "%s    %s    %s"%(i[1],i[2],i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')


if __name__ == '__main__':
    main()