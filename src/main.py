import sys
import os
import json
import threading
from dotenv import load_dotenv
from adapters.rabbitmq_adapter import RabbitMQAdapter
from adapters.mongodb_adapter import MongoDBAdapter
from adapters.flask_adapter import FlaskAPI
from domain.services import SensorService

def main():
    load_dotenv()

    # Configurar MongoDB
    mongo_adapter = MongoDBAdapter()
    if mongo_adapter.collection is None:
        print("Error: No se pudo inicializar MongoDB. Saliendo...")
        return

    # Configurar RabbitMQ
    rabbit_adapter = RabbitMQAdapter(queue_name='api1')
    sensor_service = SensorService(repository=mongo_adapter)

    # Configurar la API
    api = FlaskAPI(repository=mongo_adapter)

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            # Verificar si los datos son nulos o en cero
            for key, value in data.items():
                if value is None or value == 0:
                    data[key] = None
            sensor_service.process_data(data)
        except Exception as e:
            print(f"Error al procesar los datos: {e}")

    threading.Thread(target=api.start, daemon=True).start()

    rabbit_adapter.consume(callback)

if __name__ == "__main__":
    main()