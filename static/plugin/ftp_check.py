from ftplib import FTP


def do(target):
    port = 21
    time_out_flag = 0
    for user in ['root', 'admin']:
        for pwd in ['asdada', 'asdasda', 'asdada', 'asdaa']:
            try:
                ftp = FTP(target, timeout=5)
                ftp.connect(target, port, 10)
                if ftp.login(user, pwd).startswith('2'):
                    return True, user + '存在弱口令: ' + pwd
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


if __name__ == '__main__':
    do('101.36.153.223')
