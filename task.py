# -*-coding:utf-8-*-
from concurrent.futures import ThreadPoolExecutor

from flask import Flask

from src.model import enum

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = enum.Env.DB_URL
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from src import mapper
from src.model.entity import db

db.init_app(flask_app)
pool = ThreadPoolExecutor(30)
pool.submit(mapper.receive_result, flask_app, 2)
pool.submit(mapper.allot_task, flask_app, 15)
pool.submit(mapper.check_running, flask_app, 110)
page_size = 20
timeout = 240


if __name__ == '__main__':
    port = 37282
    print('task server running on [%s]' % port)
    flask_app.run(host='0.0.0.0', port=port)