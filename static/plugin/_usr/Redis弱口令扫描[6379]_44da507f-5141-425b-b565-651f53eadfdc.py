# -*-coding:utf-8-*-
from redis import Redis

def do(target):
    port = '6379'
    time_out_flag = 0
    for pwd in SEC_PASSWORD:
        try:
            conn = Redis(host=target, port=port, password=pwd, socket_timeout=5, socket_connect_timeout=5)
            if conn.ping():
                return True, ("弱口令: %s" % pwd)
        except Exception as e:
            if time_out_flag > 2:
                print('connection timeout , break the loop .')
                return False, ''
            if 'Timeout' in str(e):
                time_out_flag += 1
            print(e)
    return False, ''