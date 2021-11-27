from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource
from flask_jwt_extended import JWTManager
from datetime import timedelta, datetime
from pytz import timezone
from dotenv import load_dotenv
from boto3 import resource
from os import getenv
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from .services.auth import auth_verify

from .namespaces.users import users as nsUsers

load_dotenv()
project_name = getenv('PROJECT_NAME')
jwt_secret_key = getenv('JWT_SECRET_KEY')

dynamodb = resource('dynamodb')

table = dynamodb.Table(f'{project_name}-users')


app = Flask(__name__)
CORS(app)
api = Api(app)

app.config["JWT_SECRET_KEY"] = jwt_secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)


# Namespaces
api.add_namespace(nsUsers)

@api.route('/login')
class Login(Resource):
    @api.doc('login')
    def post(self):
        data = request.get_json()        

        if 'username' not in data:
            return 'Missing username'

        elif 'password' not in data:
            return 'Missing password'

        else:
            response = table.get_item(
                Key={
                    'username': data['username']
                }
            )

            if 'Item' in response:
                item = response['Item']

                check = check_password_hash(item['password'], data['password'])
                if check == True:
                    access_token = create_access_token(identity=data['username'])
                    refresh_token = create_refresh_token(identity=data['username'])
                    return {'access_token': access_token, 'refresh_token': refresh_token}
                else:
                    return 'Password incorrect', 400
            
            else:
                return 'User not found', 400

@api.route('/change-password')
class ChangePassword(Resource):
    @api.doc('change_password')
    @auth_verify(api)
    def put(self):
        identity = get_jwt_identity()
        data = request.get_json()

        if 'new_password' not in data:
            return 'Missing new password'
        
        if 'new_password_confirmation' not in data:
            return 'Missing new password confirmation'

        data['updated_at'] = str(datetime.now(timezone('America/Sao_Paulo')))

        data['password'] = generate_password_hash(data['new_password'])

        table.update_item(
            Key={
                'username': identity
            },
            UpdateExpression='set password=:p, updated_at=:a',
            ExpressionAttributeValues={
                ':p': data['password'],
                ':a': data['updated_at']
            }
        )

        return 'Password changed', 200
