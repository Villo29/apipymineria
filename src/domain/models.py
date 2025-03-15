from dataclasses import dataclass


@dataclass
class SensorData:
    temperatura: float
    humedad_suelo: float
    luminosidad: float
    humedad: float
