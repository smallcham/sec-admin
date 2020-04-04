#SEC-资产安全扫描（弱口令、系统漏洞、WEB漏洞扫描）
---
 **SEC (SEC Is Elastic Controller)** 可用于企业对服务器资源安全进行扫描排查，可控性强、可停止运行中的扫描任务、支持分布式多节点部署，更快的扫描进度 + 节点执行信息动态反馈，快速定位漏洞。

 作者开源此应用的目的是为了方便企业管理自身的服务器资产，提高安全性，以避免不必要的损失；同时也能与大家一起探讨学习，请使用者不要用于非法目的，自觉遵守 [**《中华人民共和国网络安全法》**](http://www.cac.gov.cn/2016-11/07/c_1119867116.htm) ，一起为祖国的网络安全做贡献。

---
##系统组成介绍
SEC共分为三个项目
* [前端WEB项目](https://github.com/smallcham/sec-admin-web.git)
* [中央控制系统](https://github.com/smallcham/sec-admin.git)
* [任务执行系统](https://github.com/davytitan/sec-scannode.git)

> **前端WEB系统**
使用动静分离的方式部署， WEB页面部分使用 Vue + ElementUI 编写，所有的UI都在这个项目中。

> **中央控制系统**
使用Python3 + Flask编写，负责录入资产的端口服务发现、任务执行统计、资产管理、数据字典、漏洞插件管理、用户管理、扫描任务下发以及同步等后台实现，添加的IP会立即进行端口服务以及系统探测。

> **任务执行系统**
使用Python3编写，负责处理执行下发的扫描任务，并回馈处理结果。
执行系统以进程为执行单位，可在同一台机器部署多个进程服务，**支持多节点分布式部署**。

##部署方式（共有三种部署方式）
###一、  一键部署
一键部署已经将所有服务以及启动脚本打包成docker镜像， 可以直接运行，数据库以及相关公用服务直接打包在容器内部，不支持分布式节点扩展，可作为体验测试，**不建议直接作为生产环境使用**。
1. 首先需要安装Docker服务，Ubuntu可使用以下指令直接安装（**已经安装Docker服务并启动的直接调到第 3 步**）
Ubuntu: ```sudo apt-get -y install docker.io```
CentOS: ```sudo yum -y install docker.io```
2. 启动Docker服务（**已经安装Docker服务并启动的直接调到第 3 步**）
```sudo service docker start```
3. 启动SEC服务(**指令中8793是后台访问端口， 可根据需求修改为其他端口，NODE_COUNT 为执行节点启动的进程数，默认为3**)
```docker run -d -p 8793:80 --name sec --env NODE_COUNT=3 sec-all-in && docker logs -f sec --tail 10```
4. 服务启动后初始用户为：root， 初始密码将会打印在控制台，可在登录后修改。

###二、使用容器分布式部署（推荐）
1. 首先需要安装Docker服务，Ubuntu可使用以下指令直接安装（**已经安装Docker服务并启动的直接调到第 3 步**）
Ubuntu: ```sudo apt-get -y install docker.io```
CentOS: ```sudo yum -y install docker.io```
2. 启动Docker服务（**已经安装Docker服务并启动的直接调到第 3 步**）
```sudo service docker start```
3. 使用容器启动并初始化MySQL数据库
```docker run --name sec-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=secpassword -d mysql:5.7```
```wget https://raw.githubusercontent.com/smallcham/sec-admin/master/pack/create_db.sql```
等待半分钟，mysql启动完毕后执行
```docker exec -i sec-mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < /你下载的目录/create_db.sql```

> 如果你要使用自己现有的数据库可以直接将[create_db.sql](https://github.com/smallcham/sec-admin/blob/master/pack/create_db.sql)中的SQL执行进行初始化

4. 使用容器启动Redis
```docker run --name sec-redis -d redis```
> 你也可以使用自己现有的Redis

5. 使用容器启动SEC控制系统
```docker run```
6. 登录SEC管理系统，使用节点添加功能生成并拷贝到终端执行节点安装指令，节点支持分布式，只要保证部署服务器与控制系统以及Redis之间互通即可，当然也可以直接在同一台服务器部署

###三、不使用容器本地部署（以下示例基于Ubuntu）
1. 安装MySQL、Redis、Nodejs、npm、Nginx、Python3、pip3
各种类的系统内的安装方法都大同小异， 这里就不作详细介绍。
2. 编译Web页面项目
 ```
 * git clone https://github.com/smallcham/sec-admin-web.git
 * cd 你的项目路径/sec-admin-web/
 * npm install
 * npm run build
 * ln -s 你的项目路径/sec-admin-web/dist 你的Nginx网站目录/
```
编译好的静态文件在项目的 dist 目录
3. 运行SEC核心控制系统
```
 * git clone https://github.com/smallcham/sec-admin.git
 * cd 你的项目路径/sec-admin/
 * pip install -r requirements.txt // 找不到pip的尝试 pip3 install -r requirements.txt
 * 打开项目路径下的 src/model/enum.py 修改Env类 默认LOCAL判断内的数据库以及Redis配置为你安装的配置
 * nohup gunicorn -w 10 app:flask_app
```
4. 配置Nginx访问
> 以下配置模板供参考，端口或者目录不一样请自行修改。

```
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;

        index index.html index.htm;

        server_name _;

        location / {
		root /var/www/html/dist;
		try_files $uri $uri/ 404;
        }

        location /api/ {
                proxy_pass http://localhost:8000/;
        }

        location /static/plugin/usr/ {
                proxy_pass http://localhost:8000;
        }
}
```
配置好后记得重启nginx服务
5. 启动执行节点
```
* git clone https://github.com/davytitan/sec-scannode.git
* cd 你的项目路径/sec-scannode/
* pip install -r requirements.txt // 找不到pip的尝试 pip3 install -r requirements.txt
* 打开项目根目录的 config.py 修改redis配置为你安装的ip以及密码
* python -u scan.py
```

##功能介绍
### 插件说明
SEC支持添加自定义扫描插件脚本，目前仅支持Python语言，格式如下。
```
//target参数为扫描目标， 可以是IP也可以是域名，具体取决于资产录入的是ip还是域名
def do(target):
	if 发现漏洞:
		return True, '发现漏洞，原因***'
	else:
		return False, ''
```

可参考以下FTP弱口令扫描脚本
其中 SEC_USER_NAME、SEC_PASSWORD 为字典功能中录入的Key值，扫描节点会自动将数据字典中添加的内容以设置的分隔符或JSON格式转化为数组或字典，可以通过字典Key值直接引入使用。

```
from ftplib import FTP

def do(target):
    port = 21
    time_out_flag = 0
    for user in SEC_USER_NAME:
        print(user)
        for pwd in SEC_PASSWORD:
            print(pwd)
            try:
                ftp = FTP(target, timeout=3)
                ftp.connect(target, port, 5)
                if ftp.login(user, pwd).startswith('2'):
                    return True, '用户: ' + user + ' 存在弱口令: ' + pwd
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
```
