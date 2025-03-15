import pika
from ports.message_queue import MessageQueue
import os

class RabbitMQAdapter(MessageQueue):
    def __init__(self, queue_name: str, host: str = None):
        super().__init__()
        self.queue_name = queue_name
        self.host = host or os.getenv('RABBITMQ_HOST')
        self.port = 1883
        self.user = os.getenv('RABBITMQ_USER')
        self.password = os.getenv('RABBITMQ_PASSWORD')

    def consume(self, callback):
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name, durable=True)  # Asegúrate de que la cola sea duradera
            channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
            print('Esperando mensajes...')
            channel.start_consuming()
        except Exception as e:
            print(f"Error al consumir mensajes de RabbitMQ: {e}")