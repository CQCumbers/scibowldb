import re, flask_login
from flask import Blueprint, abort, jsonify, make_response, request, url_for
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from .models import db, Question, free_sources

api = Blueprint('api', __name__, url_prefix='/api')
regex = re.compile(r'\n\(?(?P<letter>[WXYZ])')
subs = '<br>\g<letter>'


# filter questions by category and source from database
def filter_questions(sources=None, categories=None, id_only=False):
    questions = db.session.query(Question.id if id_only else Question)
    if not flask_login.current_user.is_authenticated:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in free_sources]))
    if sources and len(sources) > 0:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in sources]))
    if categories and len(categories) > 0:
        questions = questions.filter(Question.category.in_(categories))
    return questions


def get_ids(sources=None, categories=None):
    return [res[0] for res in filter_questions(sources, categories, True).all()]


# convert questions to json and substitute external URLs
def make_public(question, html=False):
    new_question = question.as_dict()
    new_question['api_url'] = url_for('api.get_question', question_id=question.id, _external=True)
    new_question['uri'] = url_for('tossup', question_id=question.id, _external=True)
    if html:
        new_question['tossup_question'] = regex.sub(subs, question.tossup_question)
        new_question['bonus_question'] = regex.sub(subs, question.bonus_question)
    return new_question


@api.route('/questions', methods=['GET'])
def get_questions():
    questions = filter_questions().all()
    return jsonify({'questions': [make_public(q) for q in questions]})


# Filter for questions with certain attributes using post requests
@api.route('/questions', methods=['POST'])
def get_questions_filtered():
    if not request.json: abort(400)
    sources, categories = request.json.get('sources'), request.json.get('categories')
    questions = filter_questions(sources, categories).all()
    return jsonify({'questions': [make_public(q) for q in questions]})


@api.route('/questions/random', methods=['GET'])
def get_random_question():
    question = filter_questions().order_by(func.random()).first()
    return jsonify({'question': make_public(question)})


@api.route('/questions/random', methods=['POST'])
def get_random_question_filtered():
    if not request.json: abort(400)
    sources, categories = request.json.get('sources'), request.json.get('categories')
    question = filter_questions(sources, categories).order_by(func.random()).first()
    return jsonify({'question': make_public(question)})


@api.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    if not question_id in get_ids(): abort(404)
    question = db.session.query(Question).get(question_id) 
    return jsonify({'question': make_public(question)})


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
