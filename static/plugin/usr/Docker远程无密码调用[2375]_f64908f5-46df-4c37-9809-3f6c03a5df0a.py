# -*-coding:utf-8-*-
import docker


def do(target):
    port = '2375'
    try:
        client = docker.APIClient(base_url='tcp://' + target + ':' + port, timeout=5)
        client.version()
        return True, '存在Docker无密码远程调用'
    except Exception as e:
        print(e)
    return False, ''