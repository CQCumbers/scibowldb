import os
from os.path import join, dirname
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

SECRET_KEY = os.environ.get('SECRET_KEY')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlcipher://:' + DB_PASSWORD + '@//' + os.path.join(basedir, 'encrypted.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# pagination
QUESTIONS_PER_PAGE = 25;

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = [os.environ.get('MAIL_USERNAME')]

# login stuff
LOGIN_USERNAME = os.environ.get('LOGIN_USERNAME')
LOGIN_PASSWORD = os.environ.get('LOGIN_PASSWORD')
