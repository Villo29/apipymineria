import sys
import os
import json
import threading
import math
import logging
import time
from dotenv import load_dotenv
from adapters.rabbitmq_adapter import RabbitMQAdapter
from adapters.mongodb_adapter import MongoDBAdapter
from adapters.flask_adapter import FlaskAPI
from domain.services import SensorService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    # Configurar MongoDB
    mongo_adapter = MongoDBAdapter()
    if mongo_adapter.collection is None:
        logger.error("Error: No se pudo inicializar MongoDB. Saliendo...")
        return

    # Configurar RabbitMQ
    rabbit_adapter = RabbitMQAdapter(queue_name='api1')
    sensor_service = SensorService(repository=mongo_adapter)

    # Configurar la API
    api = FlaskAPI(repository=mongo_adapter)

    def callback(ch, method, properties, body):
        try:
            logger.info("\n=== DATOS RECIBIDOS DE RABBITMQ ===")
            logger.info("Datos crudos: %s", body)
            logger.info("Tipo de datos: %s", type(body))
            logger.info("Longitud: %d", len(body))
            logger.info("===============================\n")

            # Convertir bytes a string y reemplazar nan sin comillas
            body_str = body.decode('utf-8')
            body_str = body_str.replace(': nan', ': "nan"')

            data = json.loads(body_str)
            logger.info("\n=== ANÁLISIS DEL JSON RECIBIDO ===")
            logger.info("JSON completo:")
            logger.info(json.dumps(data, indent=2))

            # Convertir 'nan' strings a float NaN
            for key, value in data.items():
                if isinstance(value, str) and value.lower() == 'nan':
                    data[key] = float('nan')

            # Analizar cada campo
            logger.info("\nAnálisis de campos:")
            for key, value in data.items():
                if value is None:
                    logger.warning(f"⚠️ {key}: None (Sensor desconectado)")
                elif isinstance(value, float) and math.isnan(value):
                    logger.warning(f"⚠️ {key}: NaN (Sensor desconectado)")
                elif value == 0:
                    logger.warning(f"⚠️ {key}: 0 (Posible sensor desconectado)")
                else:
                    logger.info(f"✅ {key}: {value} (Normal)")

            logger.info("===============================\n")

            # Procesar los datos
            for key, value in data.items():
                if value is None or value == 0 or (isinstance(value, float) and math.isnan(value)):
                    data[key] = None
            processed_data = sensor_service.process_data(data)
            
            # Emitir los datos a través de WebSocket
            if processed_data:
                api.emit_new_data(processed_data)
                
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON: {e}")
            logger.error("Datos recibidos: %s", body)
        except Exception as e:
            logger.error(f"Error al procesar los datos: {e}")
            logger.error("Datos recibidos: %s", body)

    def start_rabbitmq():
        try:
            rabbit_adapter.consume(callback)
        except Exception as e:
            logger.error(f"Error en el hilo de RabbitMQ: {e}")
            # No terminamos la aplicación aquí, solo registramos el error

    # Iniciar la API en un hilo separado
    api_thread = threading.Thread(target=api.start, daemon=True)
    api_thread.start()

    # Iniciar RabbitMQ en un hilo separado
    rabbit_thread = threading.Thread(target=start_rabbitmq, daemon=True)
    rabbit_thread.start()

    try:
        # Mantener el hilo principal vivo
        while True:
            if not api_thread.is_alive():
                logger.error("El hilo de la API se ha detenido. Reiniciando...")
                api_thread = threading.Thread(target=api.start, daemon=True)
                api_thread.start()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Deteniendo la aplicación...")
        rabbit_adapter.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
