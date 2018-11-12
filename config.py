import os
from os.path import join, dirname

SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# pagination
QUESTIONS_PER_PAGE = 10;

# email server
MAILGUN_KEY = os.environ.get('MAILGUN_KEY') 
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

# login stuff
LOGIN_USERNAME = os.environ.get('LOGIN_USERNAME')
LOGIN_PASSWORD = os.environ.get('LOGIN_PASSWORD')
