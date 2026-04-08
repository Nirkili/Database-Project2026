from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)

app.config["JWT_IDENTITY_CLAIM"] = "sub"
app.config["JWT_JSON_KEY"] = "identity"

jwt = JWTManager(app)
csrf = CSRFProtect(app)


from . import views