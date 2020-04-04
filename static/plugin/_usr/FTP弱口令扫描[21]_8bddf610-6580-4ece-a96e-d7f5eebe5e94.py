# -*-coding:utf-8-*-
from ftplib import FTP

def do(target):
    port = 21
    time_out_flag = 0
    for user in SEC_USER_NAME:
        print(user)
        for pwd in SEC_PASSWORD:
            print(pwd)
            try:
                ftp = FTP(target, timeout=3)
                ftp.connect(target, port, 5)
                if ftp.login(user, pwd).startswith('2'):
                    return True, '用户: ' + user + ' 存在弱口令: ' + pwd
            except Exception as e:
                if not str(e).startswith('530'):
                    print(e)
                if e.args[0] == 113 or e.args[0] == 111 or 'timed out' in str(e):
                    time_out_flag += 1
                    if time_out_flag > 2:
                        print('connection timeout , break the loop .')
                        return False, ''
                else:
                    print(e)
    return False, ''