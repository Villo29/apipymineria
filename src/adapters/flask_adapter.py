from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar CORS
from ports.api import API

class FlaskAPI(API):
    def __init__(self, repository):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.repository = repository
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/datos', methods=['GET'])
        def get_all():
            data = self.repository.get_all()
            return jsonify(data)

        @self.app.route('/datos/filtrar', methods=['GET'])
        def filter():
            field = request.args.get('field')  # Obtener el campo a filtrar
            value = request.args.get('value')  # Obtener el valor a filtrar

            if not field or not value:
                return jsonify({"error": "Se requieren los parámetros 'field' y 'value'"}), 400

            try:
                value = float(value)  # Convertir el valor a float
            except ValueError:
                return jsonify({"error": "El valor debe ser un número"}), 400

            data = self.repository.filter_by(field, value)
            return jsonify(data)

    def start(self):
        self.app.run(port=8000)