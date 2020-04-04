# -*-coding:utf-8-*-
from paramiko import SSHClient, AutoAddPolicy


def do(target):
    port = 22
    time_out_flag = 0
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    for user in SEC_USER_NAME:
        for pwd in SEC_PASSWORD:
            try:
                client.connect(target, port, user, pwd, banner_timeout=3000, timeout=5, auth_timeout=10)
                return True, ("弱口令:%s, %s" % (user, pwd))
            except Exception as e:
                if 'timed out' in str(e):
                    time_out_flag += 1
                if time_out_flag > 2:
                    print('connection timeout , break the loop .')
                    return False, ''
                print(e)
    return False, ''