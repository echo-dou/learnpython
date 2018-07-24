# -*- coding: utf-8 -*-

import paramiko
import datetime
import threading
import time
import os
import platform

def upload(local_dir, remote_dir):
    try:
        # 判断本地文件夹是否存在
        if( os.path.exists(local_dir) == False):
            print("本地目录[%s]不存在,请检查" % local_dir)
            return ""
        # 实例化Transport
        trans = paramiko.Transport((hostname, port))
        # 建立连接
        trans.connect(username = username, password = password)
        # 实例化一个sftp对象
        sftp = paramiko.SFTPClient.from_transport(trans)

        # ssh控制台 用于执行命令
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = hostname, port = port, username = username, password = password)   

        # ssh执行命令查找远程根目录是否已存在
        stdin, stdout, stderr = ssh.exec_command('find ' + remote_dir) 
        result = stdout.read().decode('utf-8')
        # 远程根目录不存在则创建
        if len(result) == 0 :                  
            try:
                sftp.mkdir(remote_dir)
            except Exception as e:
                print(e)
        # 获取系统类型      
        plat = platform.system()     
        print("start upload at %s---------------" % time.time())
        # 遍历文件夹和文件
        for root, dirs, files in os.walk(local_dir):
            print("dirs------------------------")            
            for dir in dirs:
                local_path = os.path.join(root, dir)
                remote_path = reverse_path(plat,root,dir,local_dir,remote_dir)
                #ssh执行命令查找远程文件夹是否已存在
                stdin, stdout, stderr = ssh.exec_command('find ' + remote_path) 
                result = stdout.read().decode('utf-8')
                #远程文件夹不存在则创建
                if len(result) == 0 :                  
                    try:
                        sftp.mkdir(remote_path)
                    except Exception as e:
                        print(e)
            print("files------------------------")                                          
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = reverse_path(plat,root,file,local_dir,remote_dir)
                #ssh执行命令查找远程文件是否已存在
                stdin, stdout, stderr = ssh.exec_command('find ' + remote_file) 
                result = stdout.read().decode('utf-8')
                #远程文件不存在则上传
                if len(result) == 0 :                
                    try:
                        # 上传文件,必须是文件的完整路径,远端的目录必须已经存在
                        sftp.put(local_file, remote_file)
                    except Exception as e:
                        sftp.mkdir(os.path.split(remote_file)[0])
                        sftp.put(local_file, remote_file)
        trans.close()
        ssh.close()
        print("end upload------------------")
        # 检查本地目录下是否有complete.txt 文件，没有则继续扫描
        list = os.listdir(local_dir)
        if(('complete.txt' in list) == False):
            global timer
            #300秒扫描一次
            timer = threading.Timer(3, upload, [local_dir, remote_dir])
            timer.start()
    except Exception as e:
        print("error------------------",e)

# 根据本地服务器的不同系统，生成远程路径
def reverse_path(plat,root,path,local_dir,remote_dir):
    local_path = os.path.join(root, path)    
    if(plat=="Windows"):
        relative = local_path.replace(local_dir, '').replace('\\', '/').lstrip('/')        
    else:
        relative = local_path.replace(local_dir, '').lstrip('/')
    remote_path = os.path.join(remote_dir, relative)
    return remote_path        

if __name__ == "__main__":
    # hostname = '47.106.109.182'
    # username = 'echo'
    # password = 'echo'
    # port = 22
 
    # local_dir = r'F:\dir'
    # remote_dir = '/home/echo/upload/'

    hostname = '47.94.99.17'
    username = 'root'
    password = 'r%@dNhvy&F'
    port = 22089

    local_dir = '/home/echo/upload/'    
    remote_dir = '/root/echo/'
    timer = threading.Timer(1, upload, [local_dir, remote_dir])
    timer.start()