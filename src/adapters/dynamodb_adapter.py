from decimal import Decimal
import boto3
import os
from datetime import datetime
from domain.models import SensorData
from ports.repository import Repository


class DynamoDBAdapter(Repository):
    def __init__(self):
        self.table_name = os.getenv('DYNAMODB_TABLE', 'sensor_data')
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        print(
            f"Configuración inicial: Tabla={self.table_name}, Región={aws_region}")
        print(
            f"¿Credenciales explícitas configuradas? {'Sí' if aws_access_key_id and aws_secret_access_key else 'No'}")

        try:
            # Usar credenciales explícitas si están disponibles
            if aws_access_key_id and aws_secret_access_key:
                print("Usando credenciales explícitas del .env")
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key
                )
            else:
                print("Intentando usar credenciales del archivo ~/.aws/credentials")
                self.dynamodb = boto3.resource(
                    'dynamodb', region_name=aws_region)

            # Verificar conexión a DynamoDB
            self.table = self.dynamodb.Table(self.table_name)
            table_desc = self.table.table_status
            print(f"Conexión exitosa a la tabla. Estado: {table_desc}")

        except Exception as e:
            print(f"Error al inicializar conexión con DynamoDB: {e}")
            raise

    def save(self, data: SensorData):
        try:
            item = {
                'timestamp': datetime.utcnow().isoformat(),
                'temperatura': Decimal(str(data.temperatura)),
                'humedad': Decimal(str(data.humedad)),
                'luminosidad': Decimal(str(data.luminosidad))
            }
            self.table.put_item(Item=item)
        except Exception as e:
            print(f"Error al guardar en DynamoDB: {e}")

    def get_all(self):
        response = self.table.scan()
        return response['Items']

    def filter_by(self, field: str, value: float):
        response = self.table.scan(
            FilterExpression=f"{field} = :value",
            ExpressionAttributeValues={":value": Decimal(
                str(value))}  # Convertir a Decimal
        )
        return response['Items']
