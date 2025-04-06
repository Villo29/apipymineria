# API de Monitoreo de Sensores

Esta API permite el monitoreo en tiempo real de sensores ambientales (temperatura, humedad, luminosidad y humedad del suelo) utilizando WebSockets para comunicación en tiempo real.

## Características

- Monitoreo en tiempo real de sensores
- Almacenamiento de datos en MongoDB
- Comunicación con sensores a través de RabbitMQ
- API REST para consulta de datos históricos
- WebSockets para actualizaciones en tiempo real
- Interfaz web para visualización de datos

## Tecnologías Utilizadas

### Backend
- **Python 3.8+**: Lenguaje principal de programación
- **Flask**: Framework web para la API REST
- **Flask-SocketIO**: Extensión para WebSockets
- **PyMongo**: Driver oficial de MongoDB para Python
- **Pika**: Cliente Python para RabbitMQ
- **python-dotenv**: Manejo de variables de entorno
- **Flask-CORS**: Manejo de CORS para la API

### Base de Datos
- **MongoDB**: Base de datos NoSQL
  - No se utiliza un ORM tradicional, sino el driver oficial PyMongo
  - Patrón Repository para abstraer la capa de datos
  - Colecciones flexibles para almacenamiento de datos de sensores

### Mensajería
- **RabbitMQ**: Sistema de mensajería
  - Colas duraderas para garantizar la entrega de mensajes
  - Protocolo AMQP para comunicación con sensores
  - Autenticación básica para seguridad

### Frontend
- **HTML5**: Estructura de la interfaz
- **CSS3**: Estilos y diseño responsivo
- **JavaScript**: Lógica del cliente
- **Socket.IO Client**: Comunicación en tiempo real
- **Fetch API**: Peticiones HTTP a la API REST

### Arquitectura
- **Arquitectura Hexagonal (Ports & Adapters)**: 
  - Separación clara de responsabilidades
  - Adaptadores para diferentes tecnologías
  - Dominio aislado de detalles técnicos
- **Patrones de Diseño**:
  - Repository Pattern
  - Adapter Pattern
  - Observer Pattern (para WebSockets)

### Herramientas de Desarrollo
- **Git**: Control de versiones
- **VS Code**: Editor de código
- **pip**: Gestor de paquetes Python
- **MongoDB Compass**: Interfaz gráfica para MongoDB
- **RabbitMQ Management**: Panel de control para RabbitMQ

## Estructura del Proyecto

```
src/
├── adapters/
│   ├── flask_adapter.py    # Adaptador de Flask para la API REST y WebSockets
│   ├── mongodb_adapter.py  # Adaptador para MongoDB
│   └── rabbitmq_adapter.py # Adaptador para RabbitMQ
├── domain/
│   ├── models.py           # Modelos de datos
│   └── services.py         # Lógica de negocio
├── ports/
│   ├── api.py             # Interfaz de API
│   ├── repository.py      # Interfaz de repositorio
│   └── message_queue.py   # Interfaz de cola de mensajes
├── frontend/
│   └── index.html         # Interfaz web
└── main.py                # Punto de entrada de la aplicación
```

## Requisitos

- Python 3.8+
- MongoDB
- RabbitMQ
- Dependencias de Python (ver requirements.txt)

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno (.env):
```
MONGODB_URI=mongodb://tu_uri_de_mongodb
MONGODB_DATABASE=nombre_base_datos
MONGODB_COLLECTION=nombre_coleccion
RABBITMQ_HOST=tu_host_rabbitmq
RABBITMQ_USER=usuario_rabbitmq
RABBITMQ_PASSWORD=contraseña_rabbitmq
```

## Uso

### Iniciar el Servidor

```bash
python src/main.py
```

### API REST

#### Obtener todos los datos
```
GET /datos
```

#### Obtener un dato por ID
```
GET /datos/<id>
```

#### Filtrar datos por campo y valor
```
GET /datos/filtrar?field=<campo>&value=<valor>
```

#### Crear nuevo dato
```
POST /datos
Content-Type: application/json

{
    "temperatura": 25.5,
    "humedad": 60.0,
    "luminosidad": 1000.0,
    "humedad_suelo": 40.0
}
```

#### Actualizar dato existente
```
PUT /datos/<id>
Content-Type: application/json

{
    "temperatura": 26.0
}
```

#### Eliminar dato
```
DELETE /datos/<id>
```

### WebSockets

La API proporciona un endpoint de WebSocket para recibir actualizaciones en tiempo real:

```
ws://localhost:8029
```

Eventos:
- `connect`: Cuando un cliente se conecta
- `disconnect`: Cuando un cliente se desconecta
- `new_data`: Cuando llegan nuevos datos de sensores

### Frontend

El frontend está disponible en:
```
http://localhost:8029
```

Características:
- Visualización en tiempo real de datos
- Indicador de estado de conexión
- Filtrado de datos por campo y valor
- Alertas visuales para sensores desconectados

## Modelo de Datos

```python
class SensorData:
    temperatura: float      # Temperatura en grados Celsius
    humedad_suelo: float    # Humedad del suelo en porcentaje
    luminosidad: float      # Luminosidad en lux
    humedad: float          # Humedad ambiental en porcentaje
    timestamp: datetime     # Fecha y hora de la medición
```

## Manejo de Errores

- Los sensores desconectados se marcan con `null` o `0`
- Se generan alertas visuales en el frontend
- Los errores de conexión se registran en la consola
- Se manejan errores de serialización JSON

## Seguridad

- CORS configurado para permitir conexiones desde cualquier origen
- Autenticación básica para RabbitMQ
- Conexión segura a MongoDB

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles. 