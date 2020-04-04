from os import environ


class TaskState:
    READY = 'READY'
    RUN_ABLE = 'RUN_ABLE'
    RUNNING = 'RUNNING'
    FINISH = 'FINISH'
    FAIL = 'FAIL'
    CANCEL = 'CANCEL'


class HandleState:
    UNTREATED = 'UNTREATED'
    TREATED = 'TREATED'


class TaskCron:
    ONCE = 'ONCE'
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'


class UserState:
    BANED = 'BANED'
    NORMAL = 'NORMAL'


class UserType:
    ROOT = 'ROOT'
    NORMAL = 'NORMAL'


class QueuePriority:
    MAX = 3
    HIGH = MAX
    MIDDLE = 2
    LOWER = 1


class Env:
    env = environ.get('ENV', 'LOCAL')

    if env == 'LOCAL':
        DB_URL = 'mysql+pymysql://' + environ.get('DB_URL', 'root:secpassword@localhost:3306/sec')  # eg: user:pass@ip:port/db
        RDS_URL = environ.get('RDS_URL', '0:secpassword@localhost:6379')  # eg: pass@ip:port/db
        HOST = environ.get('HOST', 'http://localhost:5000')
    elif env == 'ALL_IN':
        DB_URL = 'mysql://root@localhost:3306/sec'
        RDS_URL = '0@localhost:6379'
        HOST = 'http://localhost:8000'
    else:
        DB_URL = 'mysql+pymysql://' + environ.get('DB_URL', 'root:secpassword@localhost:3306/sec')  # eg: user:pass@ip:port/db
        RDS_URL = environ.get('RDS_URL', '0:secpassword@localhost:6379')  # eg: pass@ip:port/db
        HOST = environ.get('HOST', 'http://localhost:8000')

    SCRIPT_SRC = 'static/plugin/usr/'
    PLUGIN_SRC = HOST + '/' + SCRIPT_SRC
    TASK_PREFIX = 'task_'
    CHECK_TASK_ALIVE_SEC = 5


class RabbitConfig:
    MQ_URL = environ.get('MQ_URL', 'test:88888888@172.22.139.13:5672')  # eg: user:pass@ip:port
    info = MQ_URL.split(':')
    user = info[0]
    port = int(info[2])
    _info = info[1].split('@')
    password = _info[0]
    host = _info[1]


class RedisConfig:
    info = Env.RDS_URL.split('@')
    _info = info[0].split(':')
    if len(_info) != 2:
        db = 0
        password = ''
    else:
        db = _info[0]
        password = _info[1]

    __info = info[1].split(':')

    host = __info[0]
    port = __info[1]
