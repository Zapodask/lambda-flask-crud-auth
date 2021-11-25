from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from .routes import users as nsUsers

app = Flask(__name__)
CORS(app)
api = Api(app)

# Namespaces
api.add_namespace(nsUsers)
