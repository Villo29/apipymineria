from dataclasses import dataclass

@dataclass
class SensorData:
    temperatura: float
    humedad: float
    luminosidad: float