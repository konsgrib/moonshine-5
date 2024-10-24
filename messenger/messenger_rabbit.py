import os
from typing import List
import pika
import json
from dotenv import load_dotenv
import time

from .abstract_messenger import AbstractMessenger

# from command_factory import Command

env_path = os.path.abspath(".env")

load_dotenv(env_path)


class QueueProcessorRabbit:
    def __init__(self):
        self.login = os.getenv("RABBIT_LOGIN")
        self.password = os.getenv("RABBIT_PASSWORD")
        self.credentials = pika.PlainCredentials(self.login, self.password)

    def run_consumer(self, command):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", credentials=self.credentials)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange="moonshine", exchange_type="fanout")

        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange="moonshine", queue=queue_name)

        def callback(ch, method, properties, body):
            message = json.loads(body)
            for cmd in command:
                cmd.execute(message)
            print(f" [x] {message}")

        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )

        channel.start_consuming()

    def get_message(self, timeout=15):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", credentials=self.credentials)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange="moonshine", exchange_type="fanout")

        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange="moonshine", queue=queue_name)

        start_time = time.time()
        while time.time() - start_time < timeout:
            method_frame, header_frame, body = channel.basic_get(queue=queue_name)
            if method_frame:
                channel.basic_ack(method_frame.delivery_tag)
                message = json.loads(body)
                connection.close()
                return message

        connection.close()

    def produce_message(self, data):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", credentials=self.credentials)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange="moonshine", exchange_type="fanout")
        message = json.dumps(data)

        channel.basic_publish(exchange="moonshine", routing_key="", body=message)
        print(f" [x] Sent {message}")
        connection.close()
