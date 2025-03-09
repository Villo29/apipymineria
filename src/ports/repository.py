from abc import ABC, abstractmethod
from domain.models import SensorData

class Repository(ABC):
    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id: str):
        pass

    @abstractmethod
    def filter_by(self, field: str, value: float):
        pass

    @abstractmethod
    def create(self, data: dict):
        pass

    @abstractmethod
    def update(self, id: str, updated_data: dict):
        pass

    @abstractmethod
    def delete(self, id: str):
        pass