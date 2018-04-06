import random, re, flask_login
from flask import Blueprint, abort, jsonify, make_response, request, url_for
from sqlalchemy import or_
from .models import Question, free_sources

api = Blueprint('api', __name__, url_prefix='/api')


# filter questions by category and source from database
def filter_questions(params, attemptAuth=True):
    questions = Question.query
    if not attemptAuth or not flask_login.current_user.is_authenticated:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in free_sources]))
    if params.get('categories') and len(params['categories']) > 0:
        questions = questions.filter(Question.category.in_(params['categories']))
    if params.get('sources') and len(params['sources']) > 0:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in params['sources']]))
    return questions


# convert questions to json and substitute external URLs
def make_public(question, html=False):
    new_question = {}
    for field, value in question.as_dict().items():
        if field == 'id':
            new_question['api_url'] = url_for('api.get_question', question_id=question.id, _external=True)
            new_question['uri'] = url_for('tossup', question_id=question.id, _external=True)
        new_question[field] = value
        if html:
            new_question['tossup_question'] = re.sub(r'\n\(?(?P<letter>[WXYZ])', r'<br>\g<letter>', question.tossup_question)
            new_question['bonus_question'] = re.sub(r'\n\(?(?P<letter>[WXYZ])', r'<br>\g<letter>', question.bonus_question)
    return new_question


@api.route('/questions', methods=['GET'])
def get_questions():
    questions = filter_questions({}, attemptAuth=False)
    return jsonify({'questions': [make_public(q) for q in questions]})


# Filter for questions with certain attributes using post requests
@api.route('/questions', methods=['POST'])
def get_questions_filtered():
    if not request.json: abort(400)
    questions = filter_questions(request.json, attemptAuth=False).all()
    return jsonify({'questions': [make_public(q) for q in questions]})


@api.route('/questions/random', methods=['GET'])
def get_random_question():
    questions = filter_questions({}, attemptAuth=False)
    question = random.choice(questions)
    return jsonify({'question': make_public(question)})


@api.route('/questions/random', methods=['POST'])
def get_random_question_filtered():
    if not request.json: abort(400)
    question = random.choice(filter(request.json, attemptAuth=False).all())
    return jsonify({'question': make_public(question)})


@api.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question not in filter({}, attemptAuth=False): abort(404)
    return jsonify({'question': make_public(question)})


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
