from abc import ABC, abstractmethod

class API(ABC):
    @abstractmethod
    def start(self):
        """Inicia la API."""
        pass