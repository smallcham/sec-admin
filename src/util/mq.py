import pika
import pika.exceptions
from src.model.enum import QueuePriority, RabbitConfig
from threading import Thread

credentials = pika.PlainCredentials(username=RabbitConfig.user, password=RabbitConfig.password)


def _get_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RabbitConfig.host, RabbitConfig.port, credentials=credentials))
    return connection, connection.channel()


def publish(msg, queue=None, priority=QueuePriority.MIDDLE):
    connection, channel = _get_connection()
    channel.queue_declare(queue=queue, arguments={'x-max-priority': QueuePriority.MAX})
    properties = pika.spec.BasicProperties()
    properties.priority = priority
    channel.basic_publish(exchange='', routing_key=queue, body=msg, properties=properties)
    connection.close()


def call(ch, method, properties, body):
    print(" [x] Received %r" % body)


# def receive(func, queue=None, ack=True):
#     Thread(target=_receive, args=[func, queue, ack]).start()


# def receive_exchange(func, exchange=None, ack=True):
#     Thread(target=_receive_exchange, args=[func, exchange, ack]).start()


def receive_exchange(func, exchange=None, ack=True):
    connection, channel = _get_connection()
    channel.exchange_declare(exchange=exchange, exchange_type='fanout', durable=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=func, auto_ack=ack)
    channel.start_consuming()


def receive(func, queue=None, ack=True):
    connection, channel = _get_connection()
    try:
        channel.basic_consume(queue=queue, on_message_callback=func, auto_ack=ack)
    except pika.exceptions.ChannelClosedByBroker as e:
        print(e)
        connection, channel = _get_connection()
        channel.queue_declare(queue=queue, arguments={'x-max-priority': QueuePriority.MAX})
        channel.basic_consume(queue=queue, on_message_callback=func, auto_ack=ack)
    channel.start_consuming()


if __name__ == '__main__':
    # import uuid
    # import json
    # publish(json.dumps({
    #     'id': uuid.uuid4().__str__(),
    #     'url': 'http://172.22.147.21:5000/static/plugin/' + 'test123_e1d92754-8be2-4516-b57c-df975a7aacd0.py',
    #     'name': 'test123_e1d92754-8be2-4516-b57c-df975a7aacd0',
    #     'ip': '172.22.147.21',
    #     'port': '22',
    #     'timeout': 1000
    # }), 'dev_scan_queue')
    # # publish('test2', 'hello', priority=QueuePriority.HIGH)
    # # publish('test3', 'hello')
    #
    # import time
    # time.sleep(30)

    _receive_exchange(call, 'dev_result_exchange')
    # receive(call, 'hello1')
    # receive(call, 'hello1')
