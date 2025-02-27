import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='datos_sensores')

mensaje = {
    "temperatura": 22.5,
    "humedad": 46.7,
    "luminosidad": 22.09
}

channel.basic_publish(
    exchange='',
    routing_key='datos_sensores',
    body=json.dumps(mensaje))
print("Mensaje enviado:", mensaje)

connection.close()