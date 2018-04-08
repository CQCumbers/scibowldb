from app import app
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import make_searchable, sync_trigger
from sqlalchemy_utils.types import TSVectorType
from flask_login import UserMixin

db = SQLAlchemy(app)
make_searchable(db.metadata)


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Text, index=True)
    source = db.Column(db.Text, index=True)
    tossup_format = db.Column(db.Text)
    tossup_question = db.Column(db.Text)
    tossup_answer = db.Column(db.Text)
    bonus_format = db.Column(db.Text)
    bonus_question = db.Column(db.Text)
    bonus_answer = db.Column(db.Text)
    search_vector = db.Column(TSVectorType('tossup_question', 'tossup_answer', 'bonus_question', 'bonus_answer'))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<Question {}, {}>'.format(self.id, self.source)


class User(UserMixin):
    def get_id(self):
        return 'student'


db.configure_mappers()
db.create_all()
all_sources = set([question.source.split('-')[0] for question in Question.query.distinct(Question.source)])
all_categories = set([question.category for question in Question.query.distinct(Question.category)])
free_sources = set(['Official', '98Nats', '05Nats', 'CSUB', '16Exchange', 'HW'])
