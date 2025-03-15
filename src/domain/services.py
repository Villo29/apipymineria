from domain.models import SensorData
from ports.repository import Repository

class SensorService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def process_data(self, data: dict):
        sensor_data = SensorData(**data)
        self.repository.create(sensor_data.__dict__)