#!/bin/bash
if [ "$UPDATE" == "yes" ];then
  cd /var/www/html/sec-admin/
  git fetch --all
  git reset --hard origin/master
  git pull
  cd /var/www/html/sec-scannode/
  git fetch --all
  git reset --hard origin/master
  git pull
  cd /var/www/html/sec-admin-web/
  git fetch --all
  git reset --hard origin/master
  git pull
fi
rm -rf /var/www/html/dist
ln -s /var/www/html/sec-admin-web/dist /var/www/html/dist
mv /var/www/html/sec-admin/static/plugin/_usr/* /var/www/html/sec-admin/static/plugin/usr/
echo -e "\n\n\033[33m waiting redis start... \033[0m\n\n"
nohup redis-server &
rm -rf /var/run/mysqld/mysqld.sock
rm -rf /var/run/mysqld/mysqld.sock.lock
echo -e "\n\n\033[33m waiting mysql start... \033[0m\n\n"
service mysql restart
echo -e "\n\n\033[33m waiting db init... \033[0m\n\n"
mysql -uroot < /var/www/html/sec-admin/pack/all-in/create_db.sql
cd /var/www/html/sec-scannode/
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
echo -e "\n\n\033[33m starting task node... \033[0m\n\n"
for i in $(seq 1 $NODE_COUNT);
do
  nohup python3 -u scan.py &
done
cd /var/www/html/sec-admin/
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
export ENV=ALL_IN
nohup gunicorn -w 10 app:flask_app >> /sec.log &
echo -e "\n\n\033[33m loading service... \033[0m\n\n"
sleep 3
/usr/sbin/nginx
if [ -e init_pwd.sh ]; then
  touch init_pwd.sh
else
  touch init_pwd.sh
  echo "#!/bin/sh" > init_pwd.sh
  echo -e "\n\n\033[33m Waiting Init System Config... \033[0m\n\n"
  curl -X POST 'http://localhost/api/system/init' >> init_pwd.sh
  sleep 3
  sh ./init_pwd.sh
fi
echo -e "\033[32m Service Started . \033[0m"
cd /var/www/html/sec-admin/
nohup python3 -u task.py &
python3 -u subscan.py
