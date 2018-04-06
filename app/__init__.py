import flask, flask_sqlalchemy, flask_login, flask_wtf.csrf, flask_limiter

app = flask.Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object('config')
csrf = flask_wtf.csrf.CSRFProtect(app)
db = flask_sqlalchemy.SQLAlchemy(app)
login_manager = flask_login.LoginManager(app)
limiter = flask_limiter.Limiter(app, key_func=flask_limiter.util.get_remote_address)

from app import models, views, api
app.register_blueprint(api.api)


@login_manager.user_loader
def load_user(user_id):
    return models.User()
