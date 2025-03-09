from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from bson.objectid import ObjectId  # Para manejar IDs de MongoDB
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

    def get_by_id(self, id):
        if self.collection is None:
            print("Error: No se pudo inicializar la colección de MongoDB")
            return None

        try:
            data = self.collection.find_one({"_id": ObjectId(id)}, {'_id': 0})
            return data
        except OperationFailure as e:
            print(f"Error al obtener el dato: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al obtener el dato: {e}")
            return None

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

    def create(self, data: dict):
        if self.collection is None:
            print("Error: No se pudo inicializar la colección de MongoDB")
            return None

        try:
            data["timestamp"] = datetime.utcnow()  # Agregar timestamp automático
            result = self.collection.insert_one(data)
            if result.inserted_id:
                data["_id"] = str(result.inserted_id)  # Convertir ObjectId a string
                return data
            else:
                return None
        except OperationFailure as e:
            print(f"Error al crear el dato: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear el dato: {e}")
            return None

    def update(self, id: str, updated_data: dict):
        if self.collection is None:
            print("Error: No se pudo inicializar la colección de MongoDB")
            return None

        try:
            result = self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": updated_data}
            )
            if result.modified_count > 0:
                updated_data["_id"] = id  # Mantener el ID original
                return updated_data
            else:
                return None
        except OperationFailure as e:
            print(f"Error al actualizar el dato: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al actualizar el dato: {e}")
            return None

    def delete(self, id: str):
        if self.collection is None:
            print("Error: No se pudo inicializar la colección de MongoDB")
            return False

        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except OperationFailure as e:
            print(f"Error al eliminar el dato: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado al eliminar el dato: {e}")
            return False