#!/usr/bin/python3
#coding-utf-8

from socket import *
import getpass
import sys

#创建网络连接
def main():
    if len(sys.argv) < 3:
        print('argv is error')
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket()
    try:
        s.connect((HOST,PORT))
    except Exception as e:
        print(e)
        return

    while True:
        print('''
            ==============Welcome=========================
            -- 1.注册       2.登录　　　　　　　3.退出 --
            ==============================================
            ''')
        try:
            cmd = int(input('请输入选项>>'))
        except Exception as e:
            print('命令错误')
            continue

        if cmd == 1:
            name = do_register(s)
            if name:
                print('注册成功，直接登录！')
                login(s,name)
            elif name == 1:
                print('用户存在！')
            else:
                print('注册失败！')
        elif cmd == 2:
            name = do_login(s)
            if name:
                print('登录成功')
                login(s,name)
            else:
                print('用户名或密码不正确,登录失败')

        elif cmd == 3:
            s.send(b'E')
            sys.exit('谢谢使用！')
        else:
            print('请输入正确选项')
            sys.stdin.flush()#清除标准输入
            continue

def do_register(s):
    while True:
        name = input('用户名:')
        passwd = getpass.getpass('密码：')
        passwd1 = getpass.getpass('确认密码：')
        if (' ' in name) or (' ' in passwd):
            print('用户名与密码不允许有空格！')
            continue
        if passwd != passwd1:
            print('两次密码不一致！')
            continue

        msg = 'R {} {}'.format(name,passwd)
        #发送请求
        s.send(msg.encode())
        #等待回复
        data = s.recv(128).decode()
        if data == 'OK':
            return name
        elif data == 'EXISTS':
            #print("该用户已存在")
            return 1
        else:
            return 

def do_login(s):
    name = input('用户名：')
    passwd = getpass.getpass('密码：')
    msg = 'L {} {}'.format(name,passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()

    if data == 'OK':
        return name
    else:
        return 1

def login(s,name):
    while True:
        print('''
            ==============查询界面=========================
            -- 1.查词       2.历史记录　　　　　　　3.退出 --
            ==============================================
            ''')
        try:
            cmd = int(input('请输入选项>>'))
        except Exception as e:
            print('命令错误')
            continue
        if cmd not in [1,2,3]:
            print('请输入正确选项')
            sys.stdin.flush()
            continue
        elif cmd == 1:
            print('输入##退出')
            do_query(s,name)
        elif cmd == 2:
            do_hist(s,name)
        elif cmd == 3:
            return

def do_query(s,name):
    while True:
        word = input('请输入要查询的单词:')
        if word == '##':
            break
        msg = 'Q {} {}'.format(name,word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print('解释：',data)
        else:
            print(data)

def do_hist(s,name):
    msg = 'H {}'.format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == "OK":
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print(data)



if __name__ == '__main__':
    main()