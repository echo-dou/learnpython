#!/usr/bin/env python
# -*- coding=utf-8 -*-


"""
file: socketReceive.py
socket service
"""

import re
import socket
import threading
import time
import sys
import os
import struct


def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8080))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting client connection...')

    while 1:
        conn, addr = s.accept()
        print('Accept new connection from {0}'.format(addr))
        t = threading.Thread(target=deal_data, args=(conn,))
        t.start()

def deal_data(conn):
    conn.send(str.encode('Hi, Welcome to the server!'))

    while 1:
        # 接收远程发来的信息，有可能是待接收文件路径，也可能是over标志
        filepath = conn.recv(1024)
        filepath = bytes.decode(filepath).rstrip('\x00')
        # 如果收到over标志则传输完成，断开本次连接
        if(filepath == 'over'):
            print('all files send over')
            conn.close()
            break
        #如果收到文件路径，则判断该文件是否已存在，并将结果发送给远程  
        print("checking %s" % filepath)
        if(os.path.exists(filepath)):
            conn.send(str.encode("true"))   
        else:
            conn.send(str.encode("false"))
        # 文件不存在则接收文件    
        if(not os.path.exists(filepath)):                   
            fileinfo_size = struct.calcsize('i')
            buf = conn.recv(fileinfo_size)
            if buf:
                filesize = struct.unpack('i', buf)[0]  
                print('filepath is %s, filesize is %s' % (filepath, filesize))

                #判断文件夹是否存在，不存在则创建
                filedir = os.path.dirname(filepath)
                if(os.path.exists(filedir) == False):
                    os.mkdir(filedir)
                recvd_size = 0  # 定义已接收文件的大小
                fp = open(filepath, 'wb')
                print('start receiving...')

                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        data = conn.recv(1024)
                        recvd_size += len(data)
                    else:
                        data = conn.recv(filesize - recvd_size)
                        recvd_size = filesize
                    fp.write(data)
                fp.close()
                print('end receive...')


if __name__ == '__main__':
    socket_service()