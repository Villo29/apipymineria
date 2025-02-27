from flask import Flask, jsonify, request
from ports.api import API
from domain.models import SensorData

class FlaskAPI(API):
    def __init__(self, repository):
        self.app = Flask(__name__)
        self.repository = repository
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/datos', methods=['GET'])
        def get_all():
            data = self.repository.get_all()
            return jsonify(data)

        @self.app.route('/datos/filtrar', methods=['GET'])
        def filter():
            field = request.args.get('field')
            value = float(request.args.get('value'))
            data = self.repository.filter_by(field, value)
            return jsonify(data)

    def start(self):
        self.app.run(port=5000)