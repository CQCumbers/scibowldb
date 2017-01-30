from flask import abort, jsonify, make_response, request, url_for, render_template, session, redirect, flash
from app import app, db
from config import QUESTIONS_PER_PAGE
from sqlalchemy import or_
import re, random
from .models import Question

@app.route('/api/v1.0/questions/', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify({'questions': [make_public(q) for q in questions]})

@app.route('/api/v1.0/questions/random', methods=['GET'])
def get_random_question():
    question = random.choice(Question.query.all())
    return jsonify({'question': make_public(question)})

@app.route('/api/v1.0/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    return jsonify({'question': make_public(question)})

# Filter for questions with certain attributes using post requests
@app.route('/api/v1.0/questions/', methods=['POST'])
def get_questions_filtered():
    if not request.json:
        abort(400)
    questions = filter(request.json).all()
    return jsonify({'questions': [make_public(q) for q in questions]})

@app.route('/api/v1.0/questions/random', methods=['POST'])
def get_random_question_filtered():
    if not request.json:
        abort(400)
    question = random.choice(filter(request.json).all())
    return jsonify({'question': make_public(question)})

def make_public(question, html=False):
    new_question = {}
    for field in question.as_dict():
        if field == 'id':
            new_question['uri'] = url_for('get_question', question_id=question.id, _external=True)
        else:
            new_question[field] = question.as_dict()[field]
        if html:
            new_question['tossup_question'] = re.sub(r'\n\(?(?P<letter>[WXYZ])', r'<br>\g<letter>', question.tossup_question)
            new_question['bonus_question'] = re.sub(r'\n\(?(?P<letter>[WXYZ])', r'<br>\g<letter>', question.bonus_question)
    return new_question

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
@app.route('/tossup')
def tossup():
    questions = filter().all()
    # reset settings if they filter out all questions, for example if the source does not contain any questions of a particular category
    if len(questions) <= 0:
        flash("The inputted settings did not match any available questions")
        questions=Question.query.all()
        session['categories'] = []
        session['sources'] =[]
    question = random.choice(questions)
    session['question_id'] = question.id
    return render_template('tossup.html', question=make_public(question, html=True), settings=session)

@app.route('/bonus')
def bonus():
    if 'question_id' in session:
        question = Question.query.get(session['question_id'])
    else:
        questions = filter().all()
        if len(questions) <= 0:
            flash("The inputted settings did not match any available questions")
            questions=Question.query.all()
            session['categories'] = []
            session['sources'] = []
        question = random.choice(questions)
    return render_template('bonus.html', question=make_public(question, html=True), settings=session)

@app.route('/browse')
@app.route('/browse/<int:page>')
def browse(page=1):
    questions = filter()
    if 'search' in session and session['search'] is not None and len(session['search']) > 0:
        questions = questions.whoosh_search(session['search'])
    questions = questions.paginate(page, QUESTIONS_PER_PAGE, False)
    if len(questions.items) <= 0:
        flash("The inputted settings did not match any available questions")
        questions=Question.query.paginate(page, QUESTIONS_PER_PAGE, False)
        session['categories'] = []
        session['sources'] = []
        session['search'] = ''
    return render_template('browse.html', questions=[make_public(question, html=True) for question in questions.items], settings=session, pagination=questions)

@app.route('/about')
def about():
    return render_template('about.html', settings=session, num_questions=len(Question.query.all())*2) # counting both tossup and bonuses

@app.route('/settings', methods=['POST'])
def settings():
    session['categories'] = request.form.getlist('category')
    session['sources'] = request.form.getlist('source')
    return redirect(request.args.get('next') or url_for('tossup'))

@app.route('/search', methods=['POST'])
def search():
    session['search'] = request.form.get('search')
    return redirect(url_for('browse'))

def filter(params=session):
    # filter questions by category and source
    questions = Question.query
    if 'categories' in params and params['categories'] is not None and len(params['categories']) > 0:
        questions = questions.filter(Question.category.in_(params['categories']))
    if 'sources' in params and params['sources'] is not None and len(params['sources']) > 0:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in params['sources']]))
    return questions

@app.route('/report', methods=['POST'])
def report():
    question = Question.query.get(request.form.get('uri')[len(url_for('get_questions', _external=True)):])
    print(request.form.get('uri')[len(url_for('get_questions', _external=True)):])
    question.reported = True
    db.session.commit()
    flash("Thank you for reporting a question in need of improvement!")
    return redirect(request.args.get('next') or url_for('tossup'))

@app.route('/viewreports')
@app.route('/viewreports/<int:page>')
def viewreports(page=1):
    questions = Question.query.filter(Question.reported == True).all()
    return jsonify({'questions': [make_public(q) for q in questions]})

# set the secret key. keep this really secret (put somewhere more private in the future)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
