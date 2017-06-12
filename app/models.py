from app import db, app
from sqlalchemy.sql import expression
from flask_login import UserMixin
import flask_whooshalchemyplus

class Question(db.Model):
    #__tablename__ = 'question'
    __searchable__ = ['tossup_question', 'tossup_answer', 'bonus_question', 'bonus_answer']

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Text, index=True)
    source = db.Column(db.Text, index=True)
    tossup_format = db.Column(db.Text, index=True)
    tossup_question = db.Column(db.Text)
    tossup_answer = db.Column(db.Text)
    bonus_format = db.Column(db.Text, index=True)
    bonus_question = db.Column(db.Text)
    bonus_answer = db.Column(db.Text)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<Question {}, {}>'.format(self.id, self.source)

flask_whooshalchemyplus.init_app(app)

class User(UserMixin):
    def get_id(self):
        return 'student'

