import pymysql


def do(target):
    port = 3306
    time_out_flag = 0
    for user in ['root', 'admin']:
        for pwd in ['asdada', 'asdasda', 'asdada', 'asdaa']:
            try:
                pymysql.connect(host=target, port=port, user=user, password=pwd, connect_timeout=2)
                return True, ("弱口令: %s, %s" % (user, pwd))
            except Exception as e:
                if e.args[0] == 2003:
                    time_out_flag += 1
                if time_out_flag > 2:
                    print('connection timeout , break the loop .')
                    return False, ''
                print(e)
    return False, ''


if __name__ == '__main__':
    do('101.36.153.223')