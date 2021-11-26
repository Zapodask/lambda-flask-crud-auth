from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from flask_jwt_extended import JWTManager

from datetime import timedelta

from .routes import users as nsUsers

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

# Namespaces
api.add_namespace(nsUsers)
