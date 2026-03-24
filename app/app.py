from flask import Flask
from .config import Config
from connection import connection
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

#@app.route('/')