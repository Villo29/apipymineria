from abc import ABC, abstractmethod

class MessageQueue(ABC):
    @abstractmethod
    def consume(self, callback):
        pass