import pika
import json
from ports.message_queue import MessageQueue

class RabbitMQAdapter(MessageQueue):
    def __init__(self, queue_name: str, host: str = '127.0.0.1', username: str = 'guest', password: str = 'guest'):
        self.queue_name = queue_name
        self.host = host
        self.credentials = pika.PlainCredentials(username, password)  # Credenciales

    def consume(self, callback):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                credentials=self.credentials  # Usar credenciales
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name)
        channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        print('Esperando mensajes...')
        channel.start_consuming()