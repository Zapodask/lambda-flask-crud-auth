from flask_restx import Namespace, Resource, fields
from flask import request
from boto3 import resource
from datetime import datetime
from pytz import timezone


dynamodb = resource('dynamodb')
table = dynamodb.Table('table')

users = Namespace('users/', description='Users')

userReturn = users.model('User', {
    'username': fields.String(),
    'password': fields.String(),
    'created_at': fields.String()
})

userExpect = users.model('User', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

@users.route('/')
class Index(Resource):
    @users.doc('list_users')
    @users.marshal_list_with(userReturn)
    def get(self):
        response = table.scan()

        return response['Items']


    @users.doc('store_user')
    @users.expect(userExpect)
    def post(self):
        data = request.get_json()

        response = table.get_item(
            Key={
                'username': data['username']
            }
        )

        print(len(response))
        if len(response['Item']) > 0:
            return 'Username already exists', 400

        data['created_at'] = str(datetime.now(timezone('America/Sao_Paulo')))

        table.put_item(Item=data)

        return 'User created', 200



@users.route('/<str:username>')
@users.param('username', 'Usename')
@users.response(404, 'User not found')
class Id(Resource):
    @users.doc('show_user')
    @users.marshal_with(userReturn)
    def get(self, username):
        response = table.get_item(
            Key={
                'username': username
            }
        )

        return response['Item']


    @users.doc('update_user')
    @users.expect(userExpect)
    @users.marshal_with(userReturn)
    def put(self, username):
        data = request.get_json()

        table.update_item(
            Key={
                'username': username
            },
            UpdateExpression='set username=:u, password=:p',
            ExpressionAttributeValues={
                ':u': data['username'],
                ':p': data['password']
            }
        )

        response = table.get_item(
            Key={
                'username': username
            }
        )

        return response['Item']


    @users.doc('delete_user')
    def delete(self, username):
        table.delete_item(
            Key={
                'username': username
            }
        )

        return 'User deleted', 204