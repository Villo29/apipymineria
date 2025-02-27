from abc import ABC, abstractmethod
from domain.models import SensorData

class Repository(ABC):
    @abstractmethod
    def save(self, data: SensorData):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def filter_by(self, field: str, value: float):
        pass