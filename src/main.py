from adapters.rabbitmq_adapter import RabbitMQAdapter
from adapters.dynamodb_adapter import DynamoDBAdapter
from adapters.flask_adapter import FlaskAPI
from domain.services import SensorService
import json
from dotenv import load_dotenv
import os

def main():
    # Cargar variables de entorno
    load_dotenv()

    # Configurar DynamoDB (lee las variables de entorno automáticamente)
    dynamo_adapter = DynamoDBAdapter()

    # Configurar RabbitMQ
    rabbit_adapter = RabbitMQAdapter(queue_name='datos_sensores')

    # Configurar el servicio de dominio
    sensor_service = SensorService(repository=dynamo_adapter)

    # Configurar la API
    api = FlaskAPI(repository=dynamo_adapter)

    # Consumir mensajes de RabbitMQ
    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            print(f"Datos recibidos de la cola: {data}")
            # Asegúrate de que los valores sean números válidos
            sensor_data = {
                "temperatura": float(data["temperatura"]),
                "humedad": float(data["humedad"]),
                "luminosidad": float(data["luminosidad"])
            }
            sensor_service.process_data(sensor_data)
        except (ValueError, KeyError) as e:
            print(f"Error al procesar los datos: {e}")


    # Iniciar la API en un hilo separado
    import threading
    threading.Thread(target=api.start, daemon=True).start()

    # Iniciar el consumidor de RabbitMQ
    rabbit_adapter.consume(callback)

if __name__ == "__main__":
    main()