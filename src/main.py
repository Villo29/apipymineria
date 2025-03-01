import sys
import os
from adapters.rabbitmq_adapter import RabbitMQAdapter
from adapters.mongodb_adapter import MongoDBAdapter
from adapters.flask_adapter import FlaskAPI
from domain.services import SensorService
import json
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Configurar MongoDB
    mongo_adapter = MongoDBAdapter()
    if mongo_adapter.collection is None:  # Comparar con None
        print("Error: No se pudo inicializar MongoDB. Saliendo...")
        return

    # Configurar RabbitMQ
    rabbit_adapter = RabbitMQAdapter(queue_name='datos_sensores')

    # Configurar el servicio de dominio
    sensor_service = SensorService(repository=mongo_adapter)

    # Configurar la API
    api = FlaskAPI(repository=mongo_adapter)

    # Consumir mensajes de RabbitMQ
    def callback(ch, method, properties, body):
        data = json.loads(body)
        sensor_service.process_data(data)

    # Iniciar la API en un hilo separado
    import threading
    threading.Thread(target=api.start, daemon=True).start()

    # Iniciar el consumidor de RabbitMQ
    rabbit_adapter.consume(callback)

if __name__ == "__main__":
    main()