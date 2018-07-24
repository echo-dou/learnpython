# -*- coding=utf-8 -*-
import socket
import os
import sys
import struct
import platform  
import threading
import time
import datetime

def socket_client(hostname, port, local_dir, remote_dir):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    # 接收另一端发来的欢迎语确认通讯        
    welcome = sock.recv(1024)
    welcome = bytes.decode(welcome).rstrip('\x00')
    print(welcome)
    # 获取系统类型      
    plat = platform.system()   
    # 遍历文件
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file = os.path.join(root, file)
            remote_file = reverse_path(plat,root,file,local_dir,remote_dir)
            #将远程文件路径发送给另一端，另一端上判断该文件是否已存在，已存在则不发送文件
            sock.send(str.encode(remote_file))
            exists = sock.recv(1024)
            exists = bytes.decode(exists).rstrip('\x00')
            print('%s already exists? %s' % (remote_file, exists))
            if(exists=='false'):
                send_file(sock, local_file, remote_file)
    sock.send(str.encode('over'))              
    sock.close()
    # 检查本地目录下是否有complete.txt 文件，没有则继续扫描
    list = os.listdir(local_dir)
    if(('complete.txt' in list) == False):
        global timer
        #300秒扫描一次
        timer = threading.Timer(3, socket_client, [hostname, port, local_dir, remote_dir])
        timer.start()    

def send_file(sock, local_file, remote_file):
    if os.path.isfile(local_file):
        #定义定义文件信息 i表示一个int类型
        fileinfo_size = struct.calcsize('i')
        #定义文件大小
        fhead = struct.pack('i', os.stat(local_file).st_size)
        sock.send(fhead)
        print('start sending local_file: %s' % local_file)

        fp = open(local_file, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                print('%s file send over...' % local_file)
                break
            sock.send(data)

# 根据本地服务器的不同系统，生成远程路径 比如将F:\dir\txt1.txt 转换成/home/echo/upload/txt1.txt
def reverse_path(plat,root,path,local_dir,remote_dir):
    local_path = os.path.join(root, path)    
    if(plat=="Windows"):
        relative = local_path.replace(local_dir, '').replace('\\', '/').lstrip('/')        
    else:
        relative = local_path.replace(local_dir, '').lstrip('/')
    remote_path = os.path.join(remote_dir, relative)
    return remote_path 



if __name__ == '__main__':
    # local_dir = r'F:\dir'
    local_dir = '/root/echo'
    remote_dir = '/home/echo/upload/' 
    hostname = '47.106.109.182'  
    port = 8080  
    timer = threading.Timer(1, socket_client, [hostname, port, local_dir, remote_dir])
    timer.start()       