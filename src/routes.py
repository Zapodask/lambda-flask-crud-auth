from flask_restx import Namespace, Resource, fields
from flask import request
from boto3 import resource
from datetime import datetime
from pytz import timezone

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
import os

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


@users.route('/login')
class Login(Resource):
    @users.doc('login')
    def post(self):
        data = request.get_json()

        response = table.get_item(
            Key={
                'username': data['username']
            }
        )

        if data['password'] == response['password']:
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {'access_token': access_token, 'refresh_token': refresh_token}
        else:
            return 'Password incorrect', 400


@users.route('/refresh-token')
@jwt_required(refresh=True)
class RefreshToken(Resource):
    @users.doc('refresh_token')
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return {'access_token': access_token, 'refresh_token': refresh_token}


@users.route('/change-password')
@jwt_required()
class ChangePassword(Resource):
    @users.doc('update_user')
    @users.marshal_with(userModel)
    def put(self):
        identity = get_jwt_identity()
        data = request.get_json()

        response = table.get_item(
            Key={
                'username': identity
            }
        )

        check = check_password_hash(response['password'], data['password'])

        if check != True:
            return 'Wrong password', 400

        data['updated_at'] = now()

        table.update_item(
            Key={
                'username': identity
            },
            UpdateExpression='set password=:p, updated_at=:a',
            ExpressionAttributeValues={
                ':p': data['new_password'],
                ':a': data['updated_at']
            }
        )

        return 'Password changed', 200
