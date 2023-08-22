from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.auth import login_manager

app = Flask(__name__)
app.config.from_pyfile('../config.py')
db = SQLAlchemy(app)
login_manager.init_app(app)

from app import routes
