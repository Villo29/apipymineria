from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from ports.api import API
from datetime import datetime

class FlaskAPI(API):
    def __init__(self, repository):  # ✅ Corrige _init_ a __init__
        self.app = Flask(__name__)  # ✅ Corrige _name_ a __name__
        
        # ✅ CORS bien configurado para permitir todas las conexiones
        CORS(self.app, resources={r"/*": {"origins": "*"}})  
        
        # ✅ Configura SocketIO con async_mode adecuado
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode="threading")
        
        self.repository = repository
        self.setup_routes()
        self.setup_socket_events()

    def setup_socket_events(self):
        @self.socketio.on("connect")
        def handle_connect():
            print("Cliente conectado")

        @self.socketio.on("disconnect")
        def handle_disconnect():
            print("Cliente desconectado")

    def serialize_data(self, data):
        """Serializa los datos para enviarlos por WebSocket"""
        if isinstance(data, dict):
            serialized = {}
            for key, value in data.items():
                serialized[key] = value.isoformat() if isinstance(value, datetime) else value
            return serialized
        return data

    def emit_new_data(self, data):
        """Emitir nuevos datos a todos los clientes conectados"""
        serialized_data = self.serialize_data(data)
        self.socketio.emit("new_data", serialized_data)

    def setup_routes(self):
        @self.app.route("/datos", methods=["GET"])
        def get_all():
            data = self.repository.get_all()
            return jsonify(data)

        @self.app.route("/datos/<string:id>", methods=["GET"])
        def get_by_id(id):
            data = self.repository.get_by_id(id)
            return jsonify(data) if data else jsonify({"error": "Dato no encontrado"}), 404

        @self.app.route("/datos/filtrar", methods=["GET"])
        def filter():
            field = request.args.get("field")
            value = request.args.get("value")
            if not field or not value:
                return jsonify({"error": "Se requieren los parámetros 'field' y 'value'"}), 400
            try:
                value = float(value)
            except ValueError:
                return jsonify({"error": "El valor debe ser un número"}), 400
            data = self.repository.filter_by(field, value)
            return jsonify(data)

        @self.app.route("/datos", methods=["POST"])
        def create():
            new_data = request.json
            if not new_data:
                return jsonify({"error": "Se requieren datos en el cuerpo de la solicitud"}), 400
            try:
                created_data = self.repository.create(new_data)
                self.emit_new_data(created_data)
                return jsonify(created_data), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route("/datos/<string:id>", methods=["PUT"])
        def update(id):
            updated_data = request.json
            if not updated_data:
                return jsonify({"error": "Se requieren datos en el cuerpo de la solicitud"}), 400
            try:
                result = self.repository.update(id, updated_data)
                if result:
                    self.emit_new_data(result)
                    return jsonify(result)
                else:
                    return jsonify({"error": "Dato no encontrado"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route("/datos/<string:id>", methods=["DELETE"])
        def delete(id):
            try:
                result = self.repository.delete(id)
                if result:
                    return jsonify({"message": "Dato eliminado correctamente"})
                else:
                    return jsonify({"error": "Dato no encontrado"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 400

    def start(self):
        print("🚀 Servidor iniciado en http://0.0.0.0:8029")
        self.socketio.run(self.app, host="0.0.0.0", port=8029, allow_unsafe_werkzeug=True)  # ✅ Evita errores con Flask en modo debug