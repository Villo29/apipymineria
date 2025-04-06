import pika
from ports.message_queue import MessageQueue
import os
import time
import logging
from threading import Thread, Event

class RabbitMQAdapter(MessageQueue):
    def __init__(self, queue_name: str, host: str = None, max_retries: int = 5, retry_delay: int = 5):
        super().__init__()
        self.queue_name = queue_name
        self.host = host or os.getenv('RABBITMQ_HOST')
        self.port = 1883
        self.user = os.getenv('RABBITMQ_USER')
        self.password = os.getenv('RABBITMQ_PASSWORD')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None
        self.is_connected = False
        self.stop_event = Event()
        self.reconnect_thread = None
        self.callback = None

    def connect(self):
        """Establece la conexión con RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.is_connected = True
            logging.info("Conexión exitosa a RabbitMQ")
            return True
        except Exception as e:
            logging.error(f"Error al conectar a RabbitMQ: {e}")
            self.is_connected = False
            return False

    def reconnect(self):
        """Intenta reconectar a RabbitMQ"""
        retries = 0
        while not self.stop_event.is_set() and retries < self.max_retries:
            if self.connect():
                if self.callback:
                    self.start_consuming()
                return True
            retries += 1
            logging.info(f"Intento de reconexión {retries}/{self.max_retries}")
            time.sleep(self.retry_delay)
        return False

    def start_reconnect_thread(self):
        """Inicia un hilo para manejar la reconexión"""
        self.reconnect_thread = Thread(target=self.reconnect)
        self.reconnect_thread.daemon = True
        self.reconnect_thread.start()

    def start_consuming(self):
        """Inicia el consumo de mensajes"""
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=True
            )
            logging.info('Esperando mensajes...')
            self.channel.start_consuming()
        except Exception as e:
            logging.error(f"Error al consumir mensajes: {e}")
            self.is_connected = False
            self.start_reconnect_thread()

    def consume(self, callback):
        """Inicia el consumo de mensajes con manejo de reconexión"""
        self.callback = callback
        if not self.connect():
            self.start_reconnect_thread()
        else:
            self.start_consuming()

    def stop(self):
        """Detiene la conexión y el consumo de mensajes"""
        self.stop_event.set()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        if self.reconnect_thread:
            self.reconnect_thread.join()
        self.is_connected = False