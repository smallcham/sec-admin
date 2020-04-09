from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import hashlib

db = SQLAlchemy()


class Asset(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ip = db.Column(db.String())
    region = db.Column(db.String())
    tags = db.Column(db.String())
    ports = db.Column(db.String())
    os = db.Column(db.String())
    remark = db.Column(db.String())
    dns = db.Column(db.String())
    create_time = db.Column(db.DateTime())
    modify_time = db.Column(db.DateTime())

    def to_json(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'region': self.region,
            'tags': None if self.tags is None else eval(self.tags),
            'ports': None if self.ports is None else eval(self.ports),
            'os': None if self.os is None else eval(self.os),
            'remark': None if self.remark is None else eval(self.remark),
            'dns': None if self.dns is None else eval(self.dns),
            'create_time': self.create_time,
            'modify_time': self.modify_time
        }


class Plugin(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    remark = db.Column(db.String())
    publisher = db.Column(db.String())
    script = db.Column(db.String())
    label = db.Column(db.String())
    hide = db.Column(db.Integer())
    create_time = db.Column(db.DateTime())
    modify_time = db.Column(db.DateTime())

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'remark': self.remark,
            'publisher': self.publisher,
            'script': self.script,
            'label': None if self.label is None else eval(self.label),
            'create_time': self.create_time,
            'modify_time': self.modify_time
        }


class Dict(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    dict_key = db.Column(db.String())
    dict_value = db.Column(db.String())
    remark = db.Column(db.String())
    create_time = db.Column(db.DateTime())
    modify_time = db.Column(db.DateTime())

    def to_json(self):
        return {
            'id': self.id,
            'remark': self.remark,
            'dict_key': self.dict_key,
            'dict_value': self.dict_value,
            'create_time': self.create_time,
            'modify_time': self.modify_time
        }


class Task(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    task_name = db.Column(db.String())
    script = db.Column(db.String())
    script_name = db.Column(db.String())
    target = db.Column(db.String())
    state = db.Column(db.String())
    cron = db.Column(db.String())
    result = db.Column(db.String())
    result_state = db.Column(db.Boolean())
    handle_state = db.Column(db.String())
    handle_node = db.Column(db.String())
    create_time = db.Column(db.DateTime())
    modify_time = db.Column(db.DateTime())

    def to_json(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'script': self.script,
            'script_name': self.script_name,
            'target': self.target,
            'state': self.state,
            'cron': self.cron,
            'result': self.result,
            'result_state': self.result_state,
            'handle_state': self.handle_state,
            'handle_node': self.handle_node,
            'create_time': self.create_time,
            'modify_time': self.modify_time
        }


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String())
    pass_word = db.Column(db.String())
    salt = db.Column(db.String())
    state = db.Column(db.String())
    type = db.Column(db.String())
    create_time = db.Column(db.DateTime())
    modify_time = db.Column(db.DateTime())

    @staticmethod
    def encode(pwd, salt):
        md5 = hashlib.md5()
        md5.update(pwd.encode(encoding='utf-8'))
        md5.update(salt.encode(encoding='utf-8'))
        return md5.hexdigest()

    @staticmethod
    def make_salt():
        md5 = hashlib.md5()
        md5.update(str(uuid4()).encode(encoding='utf-8'))
        md5.update(str(uuid4()).encode(encoding='utf-8'))
        return md5.hexdigest()

    def to_json(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'pass_word': self.pass_word,
            'salt': self.salt,
            'state': self.state,
            'type': self.type,
            'create_time': self.create_time,
            'modify_time': self.modify_time
        }