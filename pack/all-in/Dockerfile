FROM ubuntu:18.04
COPY ./Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN apt-get -y update && apt-get -y install git python3 python3-pip curl nginx nmap redis-server mysql-server libmysqlclient-dev

LABEL version=0.1
WORKDIR /var/www/html/
RUN git clone https://github.com/aboul3la/Sublist3r.git
WORKDIR /var/www/html/Sublist3r/
RUN python3 setup.py install

WORKDIR /var/www/html/
LABEL version=2.5
RUN git clone https://github.com/smallcham/sec-admin.git && \
	git clone https://github.com/smallcham/sec-admin-web.git && \
	git clone https://github.com/wanzywang/sec-scannode.git
WORKDIR /var/www/html/sec-scannode/
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
WORKDIR /var/www/html/sec-admin/
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

LABEL version=1.2
ENV LANG=C.UTF-8
ENV MQ_SCAN_ENV=prod_scan_queue:3
ENV MQ_HEART_ENV=prod_heart_exchange:fanout
ENV MQ_RESULT_ENV=prod_result_exchange:fanout
ENV REDIS_ENV=0@localhost:6379
ENV NODE_COUNT=3
ENV HEART_RATE=60
COPY ./default /etc/nginx/sites-available/
CMD chmod +x pack/all-in/start.sh && pack/all-in/start.sh

EXPOSE 80
