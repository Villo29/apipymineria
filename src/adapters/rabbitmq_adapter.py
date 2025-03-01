import pika
from ports.message_queue import MessageQueue

class RabbitMQAdapter(MessageQueue):
    def __init__(self, queue_name: str, host: str = 'localhost'):
        self.queue_name = queue_name
        self.host = host

    def consume(self, callback):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name)
            channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
            print('Esperando mensajes...')
            channel.start_consuming()
        except Exception as e:
            print(f"Error al consumir mensajes de RabbitMQ: {e}")