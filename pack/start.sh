#!/bin/bash
if [ "$UPDATE" == "yes" ];then
  cd /var/www/html/sec-admin/
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
cd /var/www/html/sec-admin/
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
nohup gunicorn -w 10 app:flask_app >> /sec.log &
echo -e "\n\n\033[33m loading service... \033[0m\n\n"
sleep 3
/usr/sbin/nginx
if [ -e init_pwd.sh ]; then
  touch init_pwd.sh
else
  touch init_pwd.sh
  echo "#!/bin/sh" > init_pwd.sh
  echo -e "\n\n\033[33m Waiting Init Password... \033[0m\n\n"
  curl -X POST 'http://localhost/api/system/init' >> init_pwd.sh
  sleep 3
  sh ./init_pwd.sh
fi
echo -e "\033[32m Service started . \033[0m"
nohup python3 -u task.py &
python3 -u subscan.py