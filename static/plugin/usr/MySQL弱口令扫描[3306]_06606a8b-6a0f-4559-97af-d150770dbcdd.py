# -*-coding:utf-8-*-
import pymysql


def do(target):
    port = 3306
    time_out_flag = 0
    for user in SEC_USER_NAME:
        print(user)
        for pwd in SEC_PASSWORD:
            print(pwd)
            try:
                pymysql.connect(host=target, port=port, user=user, password=pwd, connect_timeout=5, read_timeout=5, write_timeout=5)
                return True, ("弱口令: %s, %s" % (user, pwd))
            except Exception as e:
                if e.args[0] == 2003 or 'time' in str(e) or 'refuse' in str(e) or 'reject' in str(e):
                    time_out_flag += 1
                if time_out_flag > 2:
                    print('connection timeout , break the loop .')
                    return False, ''
                print(e)
    return False, ''