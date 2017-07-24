from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
limiter = Limiter(app, key_func=get_remote_address)

from app import models, views
@login_manager.user_loader
def load_user(user_id):
    return models.User()
