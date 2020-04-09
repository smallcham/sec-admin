FROM ubuntu:18.04
COPY ./Shanghai /etc/localtime 
RUN echo "Asia/Shanghai" > /etc/timezone
RUN apt-get -y update && apt-get -y install git python3 python3-pip curl nginx nmap libmysqlclient-dev

LABEL version=0.1
WORKDIR /var/www/html/
RUN git clone https://github.com/aboul3la/Sublist3r.git
WORKDIR /var/www/html/Sublist3r/
RUN python3 setup.py install

WORKDIR /var/www/html/
LABEL version=0.6
RUN git clone https://github.com/smallcham/sec-admin.git && \
	git clone https://github.com/smallcham/sec-admin-web.git
WORKDIR /var/www/html/sec-admin/
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

LABEL version=2.2
ENV LANG=C.UTF-8
COPY ./default /etc/nginx/sites-available/
CMD chmod +x pack/start.sh && pack/start.sh

EXPOSE 80
