from domain.models import SensorData
from ports.repository import Repository
import math


class SensorService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def process_data(self, data: dict):
        # Verificar cada dato individualmente
        sensores_desconectados = []
        for key, value in data.items():
            if key in ['temperatura', 'humedad_suelo', 'luminosidad', 'humedad']:
                if value is None or value == 0 or (isinstance(value, float) and math.isnan(value)):
                    sensores_desconectados.append(key)
                    print(f"⚠️ ALERTA: El sensor {key} está desconectado")

        sensor_data = SensorData(**data)
        return self.repository.create(sensor_data.__dict__)
