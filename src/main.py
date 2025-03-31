import sys
import os
import json
import threading
import math
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
            print("\n=== DATOS RECIBIDOS DE RABBITMQ ===")
            print("Datos crudos:", body)
            print("Tipo de datos:", type(body))
            print("Longitud:", len(body))
            print("===============================\n")

            # Convertir bytes a string y reemplazar nan sin comillas
            body_str = body.decode('utf-8')
            body_str = body_str.replace(': nan', ': "nan"')

            data = json.loads(body_str)
            print("\n=== ANÁLISIS DEL JSON RECIBIDO ===")
            print("JSON completo:")
            print(json.dumps(data, indent=2))

            # Convertir 'nan' strings a float NaN
            for key, value in data.items():
                if isinstance(value, str) and value.lower() == 'nan':
                    data[key] = float('nan')

            # Analizar cada campo
            print("\nAnálisis de campos:")
            for key, value in data.items():
                if value is None:
                    print(f"⚠️ {key}: None (Sensor desconectado)")
                elif isinstance(value, float) and math.isnan(value):
                    print(f"⚠️ {key}: NaN (Sensor desconectado)")
                elif value == 0:
                    print(f"⚠️ {key}: 0 (Posible sensor desconectado)")
                else:
                    print(f"✅ {key}: {value} (Normal)")

            print("===============================\n")

            # Procesar los datos
            for key, value in data.items():
                if value is None or value == 0 or (isinstance(value, float) and math.isnan(value)):
                    data[key] = None
            sensor_service.process_data(data)
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print("Datos recibidos:", body)
        except Exception as e:
            print(f"Error al procesar los datos: {e}")
            print("Datos recibidos:", body)

    threading.Thread(target=api.start, daemon=True).start()

    rabbit_adapter.consume(callback)


if __name__ == "__main__":
    main()
