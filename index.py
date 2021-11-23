from awsgi import response as awsgi_response
from json import dumps

from src.app import app

def handler(event, context):
    print(dumps(event))

    return awsgi_response(app, event, context)