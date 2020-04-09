# -*-coding:utf-8-*-
from concurrent.futures import ThreadPoolExecutor

from flask import Flask

from src.model import enum

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = enum.Env.DB_URL
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from src import mapper
from src.model.entity import db
from app import __add_ip_and_task
db.init_app(flask_app)
pool = ThreadPoolExecutor(5)


def __add_sub_domain_with_tasks(ip, region, tags):
    try:
        subdomains = mapper.scan_sub_domain(ip)
        for _domain in subdomains:
            __add_ip_and_task(_domain, region, tags, True, flask_app)
    except Exception as e:
        print(e)


def do_scan():
    while True:
        try:
            job = mapper.get_scan_job()
            __add_sub_domain_with_tasks(job.get('domain'), job.get('region'), job.get('tags'))
            # pool.submit(__add_sub_domain_with_tasks, job.get('domain'), job.get('region'), job.get('tags'))
        except Exception as e:
            print(e)


pool.submit(do_scan)


if __name__ == '__main__':
    port = 37281
    print('subscan server running on [%s]' % port)
    flask_app.run(host='0.0.0.0', port=port)