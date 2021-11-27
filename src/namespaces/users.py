from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from pytz import timezone
from boto3 import resource
from dotenv import load_dotenv
import os

from werkzeug.security import generate_password_hash


load_dotenv()
project_name = os.getenv('PROJECT_NAME')

dynamodb = resource('dynamodb')

table = dynamodb.Table(f'{project_name}-users')

def now():
    return str(datetime.now(timezone('America/Sao_Paulo')))

users = Namespace('users', description='Users routes')

userModel = users.model('User', {
    'username': fields.String(),
    'password': fields.String(),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True)
})


@users.route('/')
class Index(Resource):
    @users.doc('list_users')
    @users.marshal_list_with(userModel)
    def get(self):
        response = table.scan()

        return response['Items'], 200

    @users.doc('store_user')
    @users.expect(userModel)
    def post(self):
        data = request.get_json()

        data['password'] = generate_password_hash(data['password'])

        response = table.get_item(
            Key={
                'username': data['username']
            }
        )

        if 'Item' in response:
            return 'Username already exists', 400

        data['created_at'] = data['updated_at'] = now()

        table.put_item(Item=data)

        return 'User created', 200


@users.route('/<string:username>')
@users.param('username', 'Usename')
@users.response(404, 'User not found')
class Id(Resource):
    @users.doc('show_user')
    @users.marshal_with(userModel)
    def get(self, username):
        username = username.replace('%20', ' ')

        response = table.get_item(
            Key={
                'username': username
            }
        )

        if 'Item' in response:
            return response['Item'], 200
        else:
            users.abort(404, 'User not found')

    @users.doc('delete_user')
    def delete(self, username):
        username = username.replace('%20', ' ')

        table.delete_item(
            Key={
                'username': username
            }
        )

        return 'User deleted', 204




