from domain.models import SensorData
from ports.repository import Repository

class SensorService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def process_data(self, data: dict):
        sensor_data = SensorData(**data)
        self.repository.save(sensor_data)