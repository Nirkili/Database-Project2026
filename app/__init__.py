from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.config["JWT_IDENTITY_CLAIM"] = "sub"
app.config["JWT_JSON_KEY"] = "identity"

jwt = JWTManager(app)


from . import views