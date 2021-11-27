import re
from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from pytz import timezone
from boto3 import resource
from dotenv import load_dotenv
import os

from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash

from ..services.auth import auth_verify


load_dotenv()
project_name = os.getenv('PROJECT_NAME')

dynamodb = resource('dynamodb')

table = dynamodb.Table(f'{project_name}-users')

def now():
    return str(datetime.now(timezone('America/Sao_Paulo')))

users = Namespace('users', description='Users routes')

userModel = users.model('User', {
    'username': fields.String(),
    'created_at': fields.String(),
    'updated_at': fields.String()
})


@users.route('/')
class Index(Resource):
    @users.doc('list_users')
    @users.marshal_list_with(userModel)
    @auth_verify(users)
    def get(self):
        response = table.scan()

        return response['Items'], 200

    @users.doc('store_user')
    def post(self):
        data = request.get_json()

        if 'username' not in data:
            return 'Missing username', 400

        if 'password' not in data:
            return 'Missing password', 400

        if 'password_confirmation' not in data:
            return 'Missing password_confirmation', 400

        if data['password'] != data['password_confirmation']:
            return 'Passwords do not match', 400

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
    @auth_verify(users)
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
    @auth_verify(users)
    def delete(self, username):
        username = username.replace('%20', ' ')
        identity = get_jwt_identity()

        if identity != username:
            return 'Only the user can delete himself', 400

        table.delete_item(
            Key={
                'username': username
            }
        )

        return 'User deleted', 204
