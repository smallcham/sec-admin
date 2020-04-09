# -*-coding:utf-8-*-
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import requests
from IPy import IP
from flask import Flask, request, session, make_response

from src.model import enum
from static.plugin import nmap

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = '9b4f019e-6e4d-11ea-b568-37a337e922db'
flask_app.config['SQLALCHEMY_DATABASE_URI'] = enum.Env.DB_URL
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from src import mapper
from src.model import result
from src.model.entity import db

db.init_app(flask_app)
pool = ThreadPoolExecutor(100)
# pool.submit(mapper.receive_breath, flask_app)
# pool.submit(mapper.receive_result, flask_app, 2)
# pool.submit(mapper.allot_task, flask_app, 15)
# pool.submit(mapper.check_running, flask_app, 110)
page_size = 20
timeout = 240


@flask_app.before_request
def before_request():
    if request.path in ['/login', '/get/user', '/system/init']:
        pass
    elif request.path.startswith('/static/plugin/usr/'):
        pass
    elif request.path in ['/modify/type', '/get/env', '/modify/state', '/del/user', '/add/user']:
        _user = session.get('user')
        if _user.get('type') != enum.UserType.ROOT:
            return make_response('not auth', 403)
    else:
        if session.get('user') is None:
            return make_response('not login', 401)


@flask_app.route('/query/ip', methods=['GET'])
def query_ip():
    res = mapper.list_asset(page_size, request.args.get('next', 1), request.args.get('ip', ''),
                            request.args.get('region', ''), request.args.get('port', ''), request.args.get('tags', ''), request.args.get('cdn', ''))
    return result.ok(__eval_page(res))


def __eval_page(res):
    return {
        'has_next': res.has_next,
        'has_prev': res.has_prev,
        'items': [_res.to_json() for _res in res.items],
        'next_num': res.next_num,
        'page_size': page_size,
        'page': res.page,
        'pages': res.pages,
        'prev_num': res.prev_num,
        'total': res.total
    }


def __update_ports(values):
    try:
        mapper.modify_asset_ports(values[0], nmap.tcp_scan(values[0]), values[1])
    except Exception as e:
        print(e)


def __update_os(values):
    try:
        mapper.modify_asset_os(values[0], nmap.os_scan(values[0]), values[1])
    except Exception as e:
        print(e)


def __add_ip_and_tasks(ips, region, tags, scan_sub_domain):
    for _ip in ips:
        try:
            for __ip in IP(_ip):
                __add_ip_and_task(str(__ip), region, tags)
        except Exception as _:
            __add_ip_and_task(str(_ip), region, tags, True)
            if scan_sub_domain:
                mapper.add_scan_job(str(_ip), region, tags)


def __add_ip_and_task(ip, region, tags, dig=False, app=None):
    if app is not None:
        param = [(ip, app)]
        _app = app
    else:
        param = [(ip, flask_app)]
        _app = flask_app
    with _app.app_context():
        mapper.add_asset(ip, region, str(tags))
    ports_results = pool.map(__update_ports, param, timeout=timeout)
    os_results = pool.map(__update_os, param, timeout=timeout)
    pool.submit(__handle_result, ports_results, __update_ports, param)
    pool.submit(__handle_result, os_results, __update_os, param)
    if dig:
        pool.submit(__dig, ip, _app)


def __dig(domain, app):
    mapper.dig(domain, app)


def __handle_result(results, fn, args):
    try:
        for _ in results:
            pass
    except TimeoutError:
        print('scanner timeout retry .')
        pool.map(fn, args, timeout=(timeout * 2))


def __eval_ip(sip, eip):
    _ip = IP(sip)
    _ip_num = _ip.int()
    res = [_ip]
    while _ip < IP(eip):
        _ip = IP(_ip_num + 1)
        _ip_num = _ip.int()
        res.append(_ip)
    return res


@flask_app.route('/count/asset', methods=['GET'])
def count_asset():
    return result.ok({
        'asset': mapper.count_asset(),
        'running': mapper.count_task_by_state(enum.TaskState.RUNNING),
        'error': mapper.count_task_result_state(True),
        'handle': mapper.count_task_handle_state(enum.HandleState.UNTREATED)
    })


@flask_app.route('/add/ip', methods=['POST'])
def add_ip():
    asset = json.loads(request.data)
    ips = asset['ip'].split(',')
    for ip in ips:
        _ips = ip.strip().split('-')
        _size = len(_ips)
        try:
            IP(_ips[0])
        except Exception as _:
            _ips = [ip]
        if _size > 1 and '/' in ip:
            return result.fail(msg='can\'t eval "/" and "-" at the same time')
        pool.submit(_add_ip_in_thread, _ips, asset)
    return result.ok()


def _add_ip_in_thread(_ips, asset):
    try:
        with flask_app.app_context():
            if len(_ips) > 1:
                __add_ip_and_tasks(__eval_ip(_ips[0], _ips[1]), asset['region'], asset['tags'], asset['scan_sub_domain'])
            else:
                __add_ip_and_tasks(_ips, asset['region'], asset['tags'], asset['scan_sub_domain'])
    except Exception as e:
        print(e)


@flask_app.route('/del/ip', methods=['POST'])
def del_ip():
    asset = json.loads(request.data)
    mapper.del_asset(asset['ip'])
    return result.ok()


@flask_app.route('/del/ips', methods=['POST'])
def del_ip_by_query():
    asset = json.loads(request.data)
    mapper.del_assets(asset.get('ip', ''), asset.get('region', ''), asset.get('port', ''), asset.get('tags', ''))
    return result.ok()


@flask_app.route('/query/plugin', methods=['GET'])
def query_plugin():
    res = mapper.list_plugin(page_size, request.args.get('next', 1), request.args.get('title', ''))
    return result.ok(__eval_page(res))


@flask_app.route('/all/plugin', methods=['GET'])
def all_plugin():
    res = mapper.list_all_plugin(request.args.get('title', ''))
    return result.ok([_res.to_json() for _res in res])


@flask_app.route('/add/plugin', methods=['POST'])
def add_plugin():
    plugin = json.loads(request.data)
    file_name = plugin['title'] + '_' + str(uuid.uuid4())
    file_name = file_name.replace('.', '_')
    file_name += '.py'
    with open(enum.Env.SCRIPT_SRC + file_name, 'wt') as f:
        f.write(plugin['script'])
    if plugin.get('id') is not None:
        mapper.modify_plugin(plugin['id'], plugin['title'], plugin['remark'], file_name, str(plugin.get('label', [])))
    else:
        mapper.add_plugin(plugin['title'], plugin['remark'], file_name, str(plugin['label']))
    return result.ok()


@flask_app.route('/view/plugin', methods=['POST'])
def view_plugin():
    plugin = json.loads(request.data)
    plugin = mapper.get_plugin(plugin['id'])
    if plugin is None:
        return result.fail(msg='脚本不存在')
    if plugin.publisher != enum.Env.HOST:
        plugin.script = requests.get(plugin.publisher + '/' + enum.Env.SCRIPT_SRC + plugin.script).text
    else:
        with open(enum.Env.SCRIPT_SRC + plugin.script, 'rt') as f:
            plugin.script = f.read()
    return result.ok(plugin.to_json())


@flask_app.route('/del/plugin', methods=['POST'])
def del_plugin():
    _dict = json.loads(request.data)
    mapper.del_plugin(_dict['id'])
    return result.ok()


@flask_app.route('/query/dict', methods=['GET'])
def query_dict():
    res = mapper.list_dict(page_size, request.args.get('next', 1), request.args.get('dict_key', ''),
                           request.args.get('remark', ''))
    return result.ok(__eval_page(res))


@flask_app.route('/add/dict', methods=['POST'])
def add_dict():
    _dict = json.loads(request.data)
    try:
        mapper.add_dict(_dict['dict_key'], _dict['dict_value'], _dict.get('remark', _dict['dict_key']))
    except Exception as e:
        return result.fail(msg='错误: ' + str(e))
    return result.ok()


@flask_app.route('/del/dict', methods=['POST'])
def del_dict():
    _dict = json.loads(request.data)
    mapper.del_dict(_dict['dict_key'])
    return result.ok()


@flask_app.route('/add/task', methods=['POST'])
def add_task():
    task = json.loads(request.data)
    mode = task.get('mode', 0)
    if mode == 1:
        hosts = mapper.list_all_asset(task.get('ip', ''), task.get('region', ''), task.get('port', ''), task.get('tags', ''))
    else:
        hosts = task.get('ips')
    scripts = task.get('scripts')
    mapper.add_new_tasks(scripts, mode, hosts)
    return result.ok()


@flask_app.route('/query/task', methods=['GET'])
def query_task():
    res = mapper.list_task(page_size, request.args.get('next', 1), request.args.get('target', ''),
                           request.args.get('state', ''), request.args.get('result_state', ''), request.args.get('handle_node', ''))
    return result.ok(__eval_page(res))


@flask_app.route('/del/task', methods=['POST'])
def del_task():
    task = json.loads(request.data)
    mapper.del_task_by_id(task.get('id', ''))
    return result.ok()


@flask_app.route('/del/tasks', methods=['POST'])
def del_task_by_query():
    task = json.loads(request.data)
    mapper.del_task_by_query(task.get('target', ''), task.get('state', ''), task.get('result_state', ''), task.get('handle_node', ''))
    return result.ok()


@flask_app.route('/treated/task', methods=['POST'])
def treated_task():
    task = json.loads(request.data)
    mapper.treated_task(task.get('id'))
    return result.ok()


@flask_app.route('/retry/task', methods=['POST'])
def retry_task():
    task = json.loads(request.data)
    mapper.retry_task(task.get('id'))
    return result.ok()


@flask_app.route('/cancel/task', methods=['POST'])
def cancel_task():
    task = json.loads(request.data)
    mapper.cancel_task(task.get('task_name'), task.get('handle_node'), task.get('state'))
    return result.ok()


@flask_app.route('/cancel/tasks', methods=['POST'])
def cancel_tasks():
    task = json.loads(request.data)
    items = mapper.list_all_task(task.get('target', ''), task.get('state', ''), task.get('result_state', ''), task.get('handle_node', ''))
    for item in items:
        mapper.cancel_task(item.task_name, item.handle_node, item.state)
    return result.ok()


@flask_app.route('/retry/os', methods=['POST'])
def retry_os():
    asset = json.loads(request.data)
    pool.submit(__update_os, asset.get('ip'), flask_app)
    return result.ok()


@flask_app.route('/retry/scan', methods=['POST'])
def retry_scan():
    asset = json.loads(request.data)
    pool.submit(__update_ports, asset.get('ip'), flask_app)
    return result.ok()


@flask_app.route('/list/breath', methods=['GET'])
def list_breath():
    return result.ok(mapper.breath_info())


@flask_app.route('/get/env', methods=['GET'])
def get_env():
    return result.ok({
        'redis': enum.Env.RDS_URL,
        'mq': '',
        'node_version': mapper.node_version()
    })


@flask_app.route('/query/user', methods=['GET'])
def query_user():
    res = mapper.list_user(page_size, request.args.get('next', 1), request.args.get('user_name', ''),
                           request.args.get('type', ''), request.args.get('state', ''))
    return result.ok(__eval_page(res))


@flask_app.route('/add/user', methods=['POST'])
def add_user():
    user = json.loads(request.data)
    res = mapper.add_user(user_name=user.get('user_name'), pass_word=user.get('pass_word'), type=user.get('type'))
    return result.ok() if res else result.fail(msg='用户已存在')


@flask_app.route('/del/user', methods=['POST'])
def del_user():
    user = json.loads(request.data)
    mapper.del_user(user_name=user.get('user_name'))
    return result.ok()


@flask_app.route('/modify/pwd', methods=['POST'])
def modify_pwd():
    user = json.loads(request.data)
    _user = session.get('user')
    res = mapper.modify_pwd(user_name=_user.get('user_name'), new_pwd=user.get('new_pwd'))
    return result.ok() if res else result.fail(msg='用户不存在')


@flask_app.route('/modify/state', methods=['POST'])
def modify_state():
    user = json.loads(request.data)
    res = mapper.modify_state(user_name=user.get('user_name'), state=user.get('state'))
    return result.ok() if res else result.fail(msg='用户不存在')


@flask_app.route('/modify/type', methods=['POST'])
def modify_type():
    user = json.loads(request.data)
    res = mapper.modify_type(user_name=user.get('user_name'), type=user.get('type'))
    return result.ok() if res else result.fail(msg='用户不存在')


@flask_app.route('/login', methods=['POST'])
def login():
    user = json.loads(request.data)
    res = mapper.login(user_name=user.get('user_name'), pass_word=user.get('pass_word'))
    if not res:
        return result.fail(msg='用户名或密码错误')
    else:
        session['user'] = res.to_json()
        return result.ok()


@flask_app.route('/logout', methods=['POST'])
def logout():
    session['user'] = None
    return result.ok()


@flask_app.route('/get/user', methods=['GET'])
def get_user():
    user = session.get('user')
    return result.ok(user) if user is not None else result.fail()


@flask_app.route('/system/init', methods=['POST'])
def init_root():
    pwd = str(uuid.uuid4())
    res = mapper.add_user(user_name='root', pass_word=pwd, type=enum.UserType.ROOT)
    if res:
        mapper.add_dict('SEC_PASSWORD',
                        json.dumps({"type": "separate", "separate": "|", "info": "root|password|123123|123|1|password01!|root@dba|P@ssw0rd!!|qwa123|root#123|12345678|test|123qwe!@#|123456789|123321|1314520|666666|woaini|fuckyou|000000|1234567890|8888888|qwerty|1qaz2wsx|abc123|abc123456|1q2w3e4r|123qwe|159357|p@ssw0rd|p@55w0rd|password!|p@ssw0rd!|password1|!@#qwe123|123qwe!@#$|1qaz@WSX|r00t|tomcat|apache|system|123456|12345|123456789|Password|iloveyou|princess|rockyou|1234567|12345678|abc123|admin888|admin123|test|password|123456|a123456|123456a|5201314|111111|woaini1314|qq123456|123123|0|1qaz2wsx|1q2w3e4r|qwe123|7758521|caonima|123qwe|a123123|123456aa|woaini520|woaini|100200|1314520|woaini123|123321|q123456|123456789|123456789a|5211314|asd123|a123456789|z123456|asd123456|a5201314|aa123456|zhang123|aptx4869|123123a|1q2w3e4r5t|1qazxsw2|5201314a|1q2w3e|aini1314|31415926|q1w2e3r4|123456qq|woaini521|1234qwer|a111111|520520|iloveyou|abc123|110110|111111a|123456abc|w123456|7758258|123qweasd|159753|qwer1234|a000000|qq123123|zxc123|123654|abc123456|123456q|qq5201314|12345678|000000a|456852|as123456|1314521|112233|521521|qazwsx123|zxc123456|abcd1234|asdasd|666666|love1314|QAZ123|aaa123|q1w2e3|aaaaaa|a123321|123000|11111111|12qwaszx|5845201314|s123456|nihao123|caonima123|zxcvbnm123|wang123|159357|idc123" }),
                        '弱口令密码')
        mapper.add_dict('SEC_USER_NAME',
                        json.dumps({"type": "separate", "separate": "|", "info": "user|root|admin1|username1|admin|user1|administrator|system|manager|guest|ftp|account|www|wwwroot|caonima|fuckyou"}),
                        '弱口令用户名')
        mapper.add_plugin('FTP弱口令扫描[21]', 'FTP弱口令扫描[21]', 'FTP弱口令扫描[21]_8bddf610-6580-4ece-a96e-d7f5eebe5e94.py',
                          '["高危"]')
        mapper.add_plugin('MongoDB弱口令扫描[27017]', 'MongoDB弱口令扫描[27017]',
                          'MongoDB弱口令扫描[27017]_6cc1eac0-fd4a-46a1-b5d9-778f78fbaae6.py', '["高危"]')
        mapper.add_plugin('MySQL弱口令扫描[3306]', 'MySQL弱口令扫描[3306]',
                          'MySQL弱口令扫描[3306]_06606a8b-6a0f-4559-97af-d150770dbcdd.py', '["高危"]')
        mapper.add_plugin('Redis弱口令扫描[6379]', 'Redis弱口令扫描[6379]',
                          'Redis弱口令扫描[6379]_44da507f-5141-425b-b565-651f53eadfdc.py', '["高危"]')
        mapper.add_plugin('SSH弱口令扫描[22]', 'SSH弱口令扫描[22]', 'SSH弱口令扫描[22]_49145b74-a221-4a41-baf0-03b2351e4634.py',
                          '["高危"]')
        mapper.add_plugin('Docker远程无密码调用[2375]', 'Docker远程无密码调用[2375]',
                          'Docker远程无密码调用[2375]_f64908f5-46df-4c37-9809-3f6c03a5df0a.py', '["高危"]')
        mapper.add_plugin('Java反序列化代码执行[8080]', 'Java反序列化代码执行[8080]',
                          'Java反序列化代码执行[8080]_fc328c6f-a103-4152-8660-de9f2e195911.py', '["高危"]')
        mapper.add_plugin('fastcgi任意文件读取及远程任意代码执行[80]', 'fastcgi任意文件读取及远程任意代码执行[80]',
                          'fastcgi目录读取_14e0818f-cafd-4fc4-a984-260aa0016765.py', '["高危"]')
        mapper.add_plugin('WebServer任意文件读取[80]', 'WebServer任意文件读取[80]',
                          'WebServer任意文件读取[80]_c04faae4-33b6-45be-bb7c-6cace5d5d4eb.py', '["高危"]')
        return 'echo -e "\033[32m The Init Password Is : ( ' + pwd + ' ) \033[0m"'
    else:
        return ''


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0')