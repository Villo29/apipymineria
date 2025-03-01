from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from domain.models import SensorData
from ports.repository import Repository
import os

class MongoDBAdapter(Repository):
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DATABASE")
        self.collection_name = os.getenv("MONGODB_COLLECTION")
        self.client = None
        self.db = None
        self.collection = None

        try:
            # Conectar a MongoDB Atlas
            self.client = MongoClient(self.uri)
            self.client.admin.command('ping')  # Verificar conexión
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print("Conexión exitosa a MongoDB Atlas")
        except ConnectionFailure as e:
            print(f"Error de conexión a MongoDB Atlas: {e}")
        except Exception as e:
            print(f"Error inesperado al conectar a MongoDB Atlas: {e}")

    def save(self, data: SensorData):
        if self.collection is None:  # Comparar con None
            print("Error: No se pudo inicializar la colección de MongoDB")
            return

        document = {
            "temperatura": data.temperatura,
            "humedad": data.humedad,
            "luminosidad": data.luminosidad,
            "timestamp": datetime.utcnow()  # Timestamp automático
        }
        try:
            self.collection.insert_one(document)
            print("Datos guardados en MongoDB Atlas")
        except OperationFailure as e:
            print(f"Error al guardar en MongoDB Atlas: {e}")
        except Exception as e:
            print(f"Error inesperado al guardar en MongoDB Atlas: {e}")

    def get_all(self):
        if self.collection is None:  # Comparar con None
            print("Error: No se pudo inicializar la colección de MongoDB")
            return []

        try:
            return list(self.collection.find({}, {'_id': 0}))
        except OperationFailure as e:
            print(f"Error al obtener datos: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado al obtener datos: {e}")
            return []

    def filter_by(self, field: str, value: float):
        if self.collection is None:  # Comparar con None
            print("Error: No se pudo inicializar la colección de MongoDB")
            return []

        try:
            query = {field: value}
            return list(self.collection.find(query, {'_id': 0}))
        except OperationFailure as e:
            print(f"Error al filtrar datos: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado al filtrar datos: {e}")
            return []