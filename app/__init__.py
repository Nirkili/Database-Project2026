from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)
csrf = CSRFProtect(app)

from . import views