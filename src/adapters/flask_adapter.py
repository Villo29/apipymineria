from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar CORS
from ports.api import API

class FlaskAPI(API):
    def __init__(self, repository):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})  # Habilitar CORS para todas las rutas
        self.repository = repository
        self.setup_routes()

    def setup_routes(self):
        # Obtener todos los datos
        @self.app.route('/datos', methods=['GET'])
        def get_all():
            data = self.repository.get_all()
            return jsonify(data)

        # Obtener un dato por ID
        @self.app.route('/datos/<string:id>', methods=['GET'])
        def get_by_id(id):
            data = self.repository.get_by_id(id)
            if data:
                return jsonify(data)
            else:
                return jsonify({"error": "Dato no encontrado"}), 404

        # Filtrar datos por campo y valor
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

        # Crear un nuevo dato
        @self.app.route('/datos', methods=['POST'])
        def create():
            new_data = request.json  # Obtener los datos del cuerpo de la solicitud
            if not new_data:
                return jsonify({"error": "Se requieren datos en el cuerpo de la solicitud"}), 400

            try:
                created_data = self.repository.create(new_data)
                return jsonify(created_data), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        # Actualizar un dato existente
        @self.app.route('/datos/<string:id>', methods=['PUT'])
        def update(id):
            updated_data = request.json  # Obtener los datos actualizados del cuerpo de la solicitud
            if not updated_data:
                return jsonify({"error": "Se requieren datos en el cuerpo de la solicitud"}), 400

            try:
                result = self.repository.update(id, updated_data)
                if result:
                    return jsonify(result)
                else:
                    return jsonify({"error": "Dato no encontrado"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        # Eliminar un dato existente
        @self.app.route('/datos/<string:id>', methods=['DELETE'])
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
        self.app.run(host='0.0.0.0', port=8029, debug=True)