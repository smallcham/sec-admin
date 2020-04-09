from src.model.entity import *
from src.model.enum import Env, RedisConfig, TaskState, TaskCron, HandleState, UserState, UserType, CdnDefault
from datetime import datetime
import multiprocessing
from sqlalchemy import or_, func
from redis import Redis
from dns import resolver
from threading import Lock
import sublist3r
import requests
import time
import json
import re

rds = Redis(host=RedisConfig.host, port=RedisConfig.port, db=RedisConfig.db, password=RedisConfig.password)

lock = multiprocessing.Manager().Lock()
task_lock = Lock()
del_lock = Lock()

host_map = {}

global _app


def count_asset():
    return Asset.query.filter().count()


def list_asset(page_size, page, ip, region, port, tags, cdn):
    build = Asset.query.order_by(Asset.modify_time.desc())
    if ip is not None and ip != '':
        build = build.filter(Asset.ip.ilike('%' + ip + '%'))
    if region is not None and region != '':
        build = build.filter_by(region=region)
    if tags is not None and tags != '':
        build = build.filter(Asset.tags.ilike('%' + tags + '%'))
    if cdn is not None and cdn != '':
        if cdn == 'unknown':
            build = build.filter(or_(Asset.dns.ilike('%' + cdn + '%'), Asset.dns.is_(None)))
        else:
            build = build.filter(Asset.dns.ilike('%' + cdn + '%'))
    if port is not None and port != '':
        build = build.filter(
            or_(Asset.ports.ilike('%\'port\': \'' + port + '\'%'), Asset.ports.ilike('%\'name\': \'' + port + '\'%')))
    return build.paginate(int(page), page_size)


def list_all_asset(ip, region, port, tags):
    build = Asset.query
    if ip is not None and ip != '':
        build = build.filter(Asset.ip.ilike('%' + ip + '%'))
    if region is not None and region != '':
        build = build.filter_by(region=region)
    if tags is not None and tags != '':
        build = build.filter(Asset.tags.ilike('%' + tags + '%'))
    if port is not None and port != '':
        build = build.filter(
            or_(Asset.ports.ilike('%\'port\': \'' + port + '\'%'), Asset.ports.ilike('%\'name\': \'' + port + '\'%')))
    return build.all()


def add_asset(ip, region, tags):
    if Asset.query.filter_by(ip=ip).first() is not None:
        return
    db.session.add(Asset(ip=ip, region=region, tags=tags, create_time=datetime.now(), modify_time=datetime.now()))
    db.session.commit()


def del_asset(ip):
    asset = Asset.query.filter_by(ip=ip).first()
    db.session.delete(asset)
    db.session.commit()


def del_assets(ip, region, tags, port):
    build = Asset.query
    if ip is not None and ip != '':
        build = build.filter(Asset.ip.ilike('%' + ip + '%'))
    if region is not None and region != '':
        build = build.filter_by(region=region)
    if tags is not None and tags != '':
        build = build.filter(Asset.tags.ilike('%' + tags + '%'))
    if port is not None and port != '':
        build = build.filter(
            or_(Asset.ports.ilike('%\'port\': \'' + port + '\'%'), Asset.ports.ilike('%\'name\': \'' + port + '\'%')))
    build.delete(synchronize_session=False)
    db.session.commit()


def modify_asset_ports(ip, ports, app):
    with app.app_context():
        with lock:
            asset = Asset.query.filter_by(ip=ip).first()
            asset.ports = str(ports)
            asset.modify_time = datetime.now()
            db.session.commit()
            _get_web_abstract(ip, ports)


def _get_web_abstract(ip, ports):
    for port in ports:
        state = port.get('state')
        if state is None or state != 'open':
            continue
        service = port.get('service')
        if service is None:
            continue
        name = service.get('name')
        if name is None:
            continue
        if name in ['http', 'https', 'http-proxy', 'radan-http']:
            title = __get_web_abstract(ip, port.get('port'))
            if title is not None:
                asset = Asset.query.filter_by(ip=ip).first()
                asset.remark = str(title)
                db.session.commit()
                break


def __get_web_abstract(ip, port):
    try:
        html = requests.get('http://%s:%s' % (ip, port), timeout=5).content.decode('utf-8')
    except Exception as e:
        print(e)
        html = requests.get('http://%s:%s' % (ip, port), timeout=10).content.decode('utf-8')
    if html is None:
        return None
    keywords = __re_meta('[kK]eywords', html)
    desc = __re_meta('[dD]escription', html)
    title = re.search('<title>.*</title>', html)
    res = []
    if title is not None:
        res.append(title.group().strip('</title>'))

    if desc is not None and desc.lastindex >= 1:
        res.append(desc.group(1).strip('</meta>').strip('\'"'))
    if keywords is not None and keywords.lastindex >= 1:
        res.append(keywords.group(1).strip('</meta>').strip('\'"'))
    return res


def __re_meta(key, html):
    return re.search("<meta\s+name=[\"']" + key + "[\"'].*?content=[\"']([\S\s]*?)[\"'].*?[\/]?>", html)


def modify_asset_os(ip, os, app):
    with lock:
        with app.app_context():
            asset = Asset.query.filter_by(ip=ip).first()
            asset.os = str(os)
            db.session.commit()


def list_plugin(page_size, page, title):
    build = Plugin.query
    build = build.filter_by(hide=0)
    if title is not None and title != '':
        build = build.filter(Plugin.title.ilike('%' + title + '%'))
    return build.paginate(int(page), page_size)


def list_all_plugin(title):
    build = Plugin.query
    build = build.filter_by(hide=0)
    if title is not None and title != '':
        build = build.filter(Plugin.title.ilike('%' + title + '%'))
    return build.all()


def modify_plugin(id, title, remark, script, label):
    plugin = Plugin.query.filter_by(id=id).first()
    plugin.title = title
    plugin.remark = remark
    plugin.script = script
    plugin.label = label
    db.session.commit()


def add_plugin(title, remark, script, label):
    db.session.add(Plugin(title=title, remark=remark, publisher=Env.HOST, script=script, label=label, hide=0,
                          create_time=datetime.now(),
                          modify_time=datetime.now()))
    db.session.commit()


def get_plugin(id):
    return Plugin.query.filter_by(id=id).first()


def del_plugin(id):
    _plugin = Plugin.query.filter_by(id=id).first()
    _plugin.hide = 1
    db.session.commit()


def list_all_dict():
    return Dict.query.filter_by().all()


def list_all_dict_to_redis():
    dicts = Dict.query.filter_by().all()
    for _dict in dicts:
        rds.set(name=_dict.dict_key, value=_dict.dict_value)


def list_dict(page_size, page, dict_key, remark):
    build = Dict.query
    if dict_key is not None and dict_key != '':
        build = build.filter(Dict.dict_key.ilike('%' + dict_key + '%'))
    if remark is not None and remark != '':
        build = build.filter(Dict.remark.ilike('%' + remark + '%'))
    return build.paginate(int(page), page_size)


def add_dict(dict_key, dict_value, remark):
    remark = '' if remark is None else remark
    dict_value = '' if dict_value is None else dict_value
    _dict = Dict.query.filter_by(dict_key=dict_key).first()
    if _dict is not None:
        _dict.dict_key = dict_key
        _dict.dict_value = dict_value
        _dict.remark = remark
        _dict.modify_time = datetime.now()
    else:
        db.session.add(Dict(dict_key=dict_key, dict_value=dict_value, remark=remark, create_time=datetime.now(),
                            modify_time=datetime.now()))
    rds.set(name=dict_key, value=dict_value)
    db.session.commit()


def del_dict(dict_key):
    _dict = Dict.query.filter_by(dict_key=dict_key).first()
    db.session.delete(_dict)
    rds.delete(dict_key)
    db.session.commit()


def del_task(task_name):
    task = Task.query.filter_by(task_name=task_name).first()
    db.session.delete(task)
    db.session.commit()


def del_task_by_id(id):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()


def del_task_by_query(target, state, result_state, handle_node):
    build = Task.query
    build = build.filter(Task.state.notin_([TaskState.RUNNING, TaskState.RUN_ABLE, TaskState.READY]))
    if state is not None and state != '':
        build = build.filter_by(state=state)
    if handle_node is not None and handle_node != '':
        build = build.filter_by(handle_node=handle_node)
    if target is not None and target != '':
        build = build.filter(Task.target.ilike('%' + target + '%'))
    if result_state is not None and result_state != '':
        build = build.filter_by(result_state=result_state)
    build.delete(synchronize_session=False)
    db.session.commit()


def add_new_tasks(scripts, mode, hosts, cron=TaskCron.ONCE):
    db.session.bulk_save_objects([
            Task(task_name=str(uuid4()), script=Env.PLUGIN_SRC + script, script_name=script, target=host.get('ip') if mode == 0 else host.ip, state=TaskState.READY, cron=cron, create_time=datetime.now(), handle_state=HandleState.UNTREATED, modify_time=datetime.now())
            for host in hosts
                for script in scripts
        ])
    db.session.commit()


def add_new_task(task_name, script, script_name, target, cron=TaskCron.ONCE):
    add_task(task_name=task_name, script=script, script_name=script_name, target=target, state=TaskState.READY,
             cron=cron)


def add_task(task_name, script, script_name, target, state, cron):
    try:
        db.session.add(
            Task(task_name=task_name, script=script, script_name=script_name, target=target, state=state, cron=cron,
                 create_time=datetime.now(), handle_state=HandleState.UNTREATED, modify_time=datetime.now()))
        db.session.commit()
    except Exception as e:
        print(e)
        return
    # mq.publish(json.dumps({
    #     'id': task_name,
    #     'url': script,
    #     'ip': target,
    #     'name': script_name.split('.py')[0],
    # }), 'prod_scan_queue')


def touch_task_state(id, state):
    task = Task.query.filter_by(id=id).first()
    task.state = state
    db.session.commit()


def treated_task(id):
    task = Task.query.filter_by(id=id).first()
    task.handle_state = HandleState.TREATED
    db.session.commit()


def retry_task(id):
    task = Task.query.filter_by(id=id).first()
    _handle_allot(task)
    # mq.publish(json.dumps({
    #     'id': task.task_name,
    #     'url': task.script,
    #     'ip': task.target,
    #     'name': task.script_name.split('.py')[0],
    # }), 'prod_scan_queue')


def list_task(page_size, page, target, state, result_state, handle_node, random=False):
    if random:
        build = Task.query.order_by(func.rand())
    else:
        build = Task.query.order_by(Task.modify_time.desc())
    if state is not None and state != '':
        build = build.filter_by(state=state)
    if handle_node is not None and handle_node != '':
        build = build.filter_by(handle_node=handle_node)
    if target is not None and target != '':
        build = build.filter(Task.target.ilike('%' + target + '%'))
    if result_state is not None and result_state != '':
        build = build.filter_by(result_state=result_state)
    return build.paginate(int(page), page_size)


def list_all_task(target, state, result_state, handle_node):
    build = Task.query
    if state is not None and state != '':
        build = build.filter_by(state=state)
    if handle_node is not None and handle_node != '':
        build = build.filter_by(handle_node=handle_node)
    if target is not None and target != '':
        build = build.filter(Task.target.ilike('%' + target + '%'))
    if result_state is not None and result_state != '':
        build = build.filter_by(result_state=result_state)
    return build.all()


def count_task_by_state(state):
    return Task.query.filter_by(state=state).count()


def count_task_result_state(state):
    return Task.query.filter_by(result_state=state, handle_state='UNTREATED').count()


def count_task_handle_state(state):
    return Task.query.filter_by(state=state, result_state=False, handle_state='UNTREATED').count()


def breath_info():
    res = rds.keys('heart_*')
    info = []
    for _res in res:
        _info = rds.get(_res)
        task = get_new_task(_res.decode('utf-8').split('_', maxsplit=1)[1])
        if _info is None:
            info.append({
                'server': task.handle_node,
                'timespan': str(datetime.now().timestamp()),
                'active': False,
                'info': False if task is None else task.to_json()
            })
        else:
            _info = json.loads(_info)
            _info['info'] = False if task is None else task.to_json()
            info.append(_info)
    return info


# def receive_breath(interval):
#     _redis_breath_handle(interval)
# mq.receive_exchange(func=_breath_handle, exchange='prod_heart_exchange')


def receive_result(app, interval):
    global _app
    _app = app
    _redis_result_handle(app, interval)
    # mq.receive_exchange(func=_result_handle, exchange='prod_result_exchange')


def check_running(app, interval=110):
    while True:
        try:
            with app.app_context():
                tasks = list_task(page_size=50, page=1, target=None, state=TaskState.RUNNING, result_state=None,
                                  handle_node=None,
                                  random=True).items
                _handle_check_running_list(tasks)
            time.sleep(interval)
        except Exception as e:
            print(e)


def _handle_check_running_list(tasks):
    for task in tasks:
        _handle_check_running(task)


def _handle_check_running(task):
    try:
        node = rds.get('heart_' + task.handle_node)
        if not node:
            retry_task(task.id)
        else:
            node = json.loads(node)
            if ((datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   '%Y-%m-%d %H:%M:%S').timestamp() - datetime.fromtimestamp(
                float(node.get('timespan')) / 1000).timestamp()) / 60) > Env.CHECK_TASK_ALIVE_SEC:
                retry_task(task.id)
    except Exception as e:
        print(e)


def allot_task(app, interval=30):
    while True:
        try:
            with app.app_context():
                tasks = list_task(page_size=1000, page=1, target=None, state=TaskState.READY, result_state=None,
                                  handle_node=None).items
                _handle_allot_list(tasks)
        except Exception as e:
            print(e)
        time.sleep(interval)


def _handle_allot_list(tasks):
    size = len(tasks)
    if size > 0:
        print(' - allot task - size[%s]' % str(size))
    for task in tasks:
        _handle_allot(task)


def _handle_allot(task):
    try:
        task_lock.acquire(blocking=True)
        if task.state not in [TaskState.READY, TaskState.RUNNING, TaskState.FAIL, TaskState.CANCEL, TaskState.FINISH]:
            pass
        else:
            rds.set(Env.TASK_PREFIX + task.task_name, json.dumps({
                'id': task.task_name,
                'url': task.script,
                'ip': task.target,
                'name': task.script_name.split('.py')[0],
            }))
            touch_task_state(task.id, TaskState.RUN_ABLE)
    except Exception as e:
        print(e)
    finally:
        if task_lock.locked():
            task_lock.release()


def cancel_task(task_name, handle_node, mode=TaskState.READY):
    task_lock.acquire()
    try:
        if mode == TaskState.READY:
            del_task(task_name)
            pass
        elif mode == TaskState.RUN_ABLE:
            if 1 == rds.delete(Env.TASK_PREFIX + task_name):
                del_task(task_name)
        elif mode == TaskState.RUNNING:
            rds.setex(name=handle_node + '_' + 'action', value=json.dumps({'id': task_name, 'action': 'cancel'}),
                      time=600)
    except Exception as e:
        print(e)
    finally:
        if task_lock.locked():
            task_lock.release()
    return True


def get_task(handle_node, state):
    return Task.query.filter_by(handle_node=handle_node, state=state).first()


def get_new_task(handle_node):
    return Task.query.order_by(Task.modify_time.desc()).filter_by(handle_node=handle_node).first()


# def _breath_handle(ch, method, properties, body):
#     try:
#         if len(host_map) > 1000:
#             host_map.clear()
#         result = json.loads(body)
#         server = result.get('server')
#         host_map[server] = {
#             'server_name': server,
#             'timespan': datetime.fromtimestamp(float(result.get('timespan')) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
#             'active': result.get('active', True),
#             'info': result.get('info')
#         }
#     except Exception as e:
#         print('_breath_handle')
#         print(e)


def _redis_result_handle(app, interval=2):
    while True:
        try:
            with app.app_context():
                result = rds.lpop('prod_result_exchange')
                if result is None:
                    time.sleep(interval)
                    continue
                result = json.loads(result)
                print('handling task result: %s, %s' % (result.get('taskid'), result.get('taskstatus')))
                task_lock.acquire()
                task = Task.query.filter_by(task_name=result.get('taskid')).first()
                if task is None:
                    if task_lock.locked():
                        task_lock.release()
                    time.sleep(interval)
                    continue
                task.state = result.get('taskstatus')
                if task.state == TaskState.CANCEL:
                    db.session.delete(task)
                else:
                    task.result = result.get('result')
                    task.result_state = result.get('scriptstatus')
                    task.handle_node = result.get('node')
                    task.modify_time = datetime.now()
                db.session.commit()
        except Exception as e:
            print(e)
        finally:
            if task_lock.locked():
                task_lock.release()


# def _result_handle(ch, method, properties, body):
#     try:
#         global _app
#         with _app.app_context():
#             result = json.loads(body)
#             task_lock.acquire()
#             task = Task.query.filter_by(task_name=result.get('taskid')).first()
#             task.state = result.get('taskstatus')
#             if task.state == TaskState.CANCEL:
#                 db.session.delete(task)
#             else:
#                 task.result = result.get('result')
#                 task.result_state = result.get('scriptstatus')
#                 task.handle_node = result.get('node')
#                 task.modify_time = datetime.now()
#             db.session.commit()
#     except Exception as e:
#         print(e)
#     task_lock.release()


def list_user(page_size, page, user_name, type, state):
    build = User.query.order_by(User.modify_time.desc())
    if state is not None and state != '':
        build = build.filter_by(state=state)
    if type is not None and type != '':
        build = build.filter_by(type=type)
    if user_name is not None and user_name != '':
        build = build.filter(User.user_name.ilike('%' + user_name + '%'))
    return build.paginate(int(page), page_size)


def add_user(user_name, pass_word, type=UserType.NORMAL):
    if User.query.filter_by(user_name=user_name).first() is not None:
        return False
    salt = User.make_salt()
    db.session.add(
        User(user_name=user_name, pass_word=User.encode(pass_word, salt), salt=salt, state=UserState.NORMAL, type=type,
             create_time=datetime.now(), modify_time=datetime.now()))
    db.session.commit()
    return True


def del_user(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    db.session.delete(user)
    db.session.commit()


def modify_pwd(user_name, new_pwd):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        return False
    user.salt = User.make_salt()
    user.pass_word = User.encode(new_pwd, user.salt)
    user.modify_time = datetime.now()
    db.session.commit()
    return True


def modify_state(user_name, state):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        return False
    user.state = state
    user.modify_time = datetime.now()
    db.session.commit()
    return True


def modify_type(user_name, type):
    user = User.query.filter_by(user_name=user_name).first()
    if user is None:
        return False
    user.type = type
    user.modify_time = datetime.now()
    db.session.commit()
    return True


def login(user_name, pass_word):
    user = User.query.filter_by(user_name=user_name, state=UserState.NORMAL).first()
    if user is None:
        return False
    _pass_word = User.encode(pass_word, user.salt)
    return user if _pass_word == user.pass_word else False


def node_version():
    version = rds.get('node_version')
    if version is None:
        version = '1.5.1'
        rds.set('node_version', version)
    return version


def modify_dns(ip, dns):
    asset = Asset.query.filter_by(ip=ip).first()
    if asset is None:
        return False
    asset.dns = dns
    asset.modify_time = datetime.now()
    db.session.commit()
    return True


def get_cdn(cname):
    features = rds.get(CdnDefault.key)
    if features is None:
        features = CdnDefault.data
        add_dict(CdnDefault.key, json.dumps({
            'type': 'json',
            'separate': '',
            'info': json.dumps(features, ensure_ascii=False)
        }), 'CDN特征库')
    else:
        features = json.loads(features)
        features = eval(features.get('info'))

    if isinstance(features, list):
        for feature in features:
            cname_list = feature.get('cname')
            for cname_feature in cname_list:
                if cname_feature in str(cname):
                    return feature.get('name')
    return 'unknown'


def dig(domain, app):
    try:
        records = resolver.query(domain)
    except Exception as e:
        print(e)
        records = resolver.query(domain)
    if records is None:
        return
    name = records.rrset.name
    try:
        with app.app_context():
            name = str(name)
            cdn = 'unknown'
            if name.find(domain) != 0:
                cdn = get_cdn(name)
            data = {
                'cdn': cdn,
                'name': name,
                'records': []
            }
            for record in records:
                data['records'].append({
                    'target': str(record)
                })
            modify_dns(domain, json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(e)


def scan_sub_domain(domain):
    return sublist3r.main(domain, 100, None, ports=None, silent=False, verbose=False,
                          enable_bruteforce=False,
                          engines='baidu,yahoo,bing,ask,virustotal,threatcrowd,ssl,passivedns')


def add_scan_job(domain, region, tags):
    rds.rpush(Env.SUB_SCAN_TASK_QUEUE, json.dumps({'domain': domain, 'region': region, 'tags': str(tags)}))


def get_scan_job():
    return json.loads(rds.blpop(Env.SUB_SCAN_TASK_QUEUE)[1])