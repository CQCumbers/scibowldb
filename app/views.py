from flask import abort, jsonify, make_response, request, url_for, render_template, session
from app import app, db
from .models import Question
import random

@app.route('/api/v1.0/questions/', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify({'questions': [make_public(q) for q in questions]})

@app.route('/api/v1.0/questions/random', methods=['GET'])
def get_random_question():
    questions = Question.query.all()
    return jsonify({'question': random.choice([make_public(q) for q in questions])})

@app.route('/api/v1.0/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    q = Question.query.get_or_404(question_id)
    return jsonify({'question': make_public(q)})

# Filter for questions with certain attributes using post requests
@app.route('/api/v1.0/questions/', methods=['POST'])
def get_questions_filtered():
    if not request.json:
        abort(400)
    params = {}
    if 'category' in request.json:
        params['category'] = request.json['category']
    if 'source' in request.json:
        params['source'] = request.json['source']
    questions = Question.query.filter_by(**params)
    return jsonify({'questions': [make_public(q) for q in questions]})

@app.route('/api/v1.0/questions/random', methods=['POST'])
def get_random_question_filtered():
    if not request.json:
        abort(400)
    params = {}
    if 'category' in request.json:
        params['category'] = request.json['category']
    if 'source' in request.json:
        params['source'] = request.json['source']
    questions = Question.query.filter_by(**params).all()
    return jsonify({'question': random.choice([make_public(q) for q in questions])})

def make_public(question):
    new_question = {}
    for field in question.as_dict():
        if field == 'id':
            new_question['uri'] = url_for('get_question', question_id=question.id, _external=True)
        else:
            new_question[field] = question.as_dict()[field]
    return new_question

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
@app.route('/tossup')
def tossup():
    question = random.choice(list(Question.query.all()))
    session['question_id'] = question.id
    return render_template('tossup.html', question_type='tossup', question=question, settings=session)

@app.route('/bonus')
def bonus():
    if 'question_id' in session:
        question = Question.query.get(session['question_id'])
    else:
       question = random.choice(list(Question.query.all()))
    return render_template('bonus.html', question_type='bonus', question=question, settings=session)

# set the secret key.  keep this really secret: (put somewhere more private in the future)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
