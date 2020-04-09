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


class CdnDefault:
    key = 'SEC_CDN_FEATURE'
    data = [
        {"cname": ["yunjiasu-cdn.net"], "name": "百度云"},
        {'cname': ['cdntip.com', 'cdn.dnsv1.com'], 'name': '腾讯云'},
        {'cname': ['aliyuncs.com', 'aliyun-inc.com', 'alikunlun.com', 'alibabadns.com', '.aliyun.com', 'cdngslb.com', 'tbcache.com', 'alipaydns.com', 'kunlunar.com'], 'name': '阿里云'},
        {'cname': ['telefonica.com.'], 'name': 'Telefonica'},
        {'cname': ['presscdn.com'], 'name': 'Presscdn'},
        {'cname': ['anankecdn.com.br.'], 'name': 'Ananke'},
        {'cname': ['azureedge.net'], 'name': 'AzureCDN'},
        {'cname': ['bitgravity.com'], 'name': 'TataCommunications'},
        {'cname': ['skyparkcdn.net'], 'name': 'SkyparkCDN'},
        {'cname': ['speedcdns.com.', 'mwcloudcdn.com.'], 'name': 'QUANTIL'},
        {'cname': ['cdn.ngenix.net'], 'name': 'NGENIX'},
        {'cname': ['netdna-cdn.com'], 'name': 'MaxCDN'},
        {'cname': ['vo.llnwd.net'], 'name': 'Limelight'},
        {'cname': ['fpbns.net.', 'footprint.net.'], 'name': 'Level3'},
        {'cname': ['lswcdn.net'], 'name': 'Leaseweb'},
        {'cname': ['.awsdns'], 'name': 'KeyCDN'},
        {'cname': ['internapcdn.net'], 'name': 'Internap'},
        {'cname': ['incapdns.net'], 'name': 'Incapsula'},
        {'cname': ['hwcdn.net.'], 'name': 'Highwinds'},
        {'cname': ['fastly.net.'], 'name': 'Fastly'},
        {'cname': ['edgecastcdn.net.'], 'name': 'EdgeCast'},
        {'cname': ['.cdn.cloudflare.net'], 'name': 'CloudFlare'},
        {'cname': ['wscloudcdn.com.'], 'name': 'ChinaNetCenter'},
        {'cname': ['lxdns.com', 'cncssr.chinacache.net.', 'chinacache.net.', 'ccgslb.com.cn'], 'name': 'ChinaCache'},
        {'cname': ['cdnsun.net.'], 'name': 'CDNsun'},
        {'cname': ['cdnify.io'], 'name': 'CDNify'},
        {'cname': ['cdnetworks.com.gccdn.net.'], 'name': 'CDNetworks'},
        {'cname': ['cdn77.org.', 'cdn77.net.'], 'name': 'CDN77'},
        {'cname': ['cachefly.net.'], 'name': 'Cachefly'},
        {'cname': ['azioncdn.net.'], 'name': 'Azion'},
        {'cname': ['amazonaws.com', 'cloudfront.net'], 'name': 'AmazonCloudfront'},
        {'cname': ['akamai.net', 'akamaized.net', 'akamai-staging.net'], 'name': 'Akamai'},
        {'cname': ['scalabledns.com'], 'name': 'scalabledns'}
    ]


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
    SUB_SCAN_TASK_QUEUE = 'SUB_SCAN_TASK_QUEUE'
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
