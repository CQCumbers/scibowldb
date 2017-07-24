from flask import abort, jsonify, make_response, request, url_for, render_template, session, redirect, flash
from urllib.parse import urlparse, urljoin
from flask_login import current_user, login_user, logout_user, login_required
import flask_whooshalchemyplus
from app import app, db, limiter
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
import re, random, ast, requests
from .models import Question, User

with app.app_context():
    #flask_whooshalchemyplus.index_all(app)
    ALL_SOURCES = sorted(set([question.source.split('-')[0] for question in Question.query.distinct(Question.source)]))
    ALL_CATEGORIES = sorted(set([question.category for question in Question.query.distinct(Question.category)]))
    FREE_SOURCES = sorted(set(['Official', '98Nats', '05Nats', 'CSUB']))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/api/v1.0/questions/', methods=['GET'])
def get_questions():
    questions = filter(params=[],attemptAuth=False)
    return jsonify({'questions': [make_public(q) for q in questions]})

@app.route('/api/v1.0/questions/random', methods=['GET'])
def get_random_question():
    questions = filter(params=[],attemptAuth=False)
    question = random.choice(questions)
    return jsonify({'question': make_public(question)})

@app.route('/api/v1.0/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question in filter(params=[],attemptAuth=False):
        return jsonify({'question': make_public(question)})
    else:
        abort(404)

# Filter for questions with certain attributes using post requests
@app.route('/api/v1.0/questions/', methods=['POST'])
def get_questions_filtered():
    if not request.json:
        abort(400)
    questions = filter(params=request.json).all()
    return jsonify({'questions': [make_public(q) for q in questions]})

@app.route('/api/v1.0/questions/random', methods=['POST'])
def get_random_question_filtered():
    if not request.json:
        abort(400)
    question = random.choice(filter(params=request.json).all())
    return jsonify({'question': make_public(question)})

def make_public(question, html=False):
    new_question = {}
    for field in question.as_dict():
        if field == 'id':
            new_question['api_url'] = url_for('get_question', question_id=question.id, _external=True)
            new_question['uri'] = url_for('tossup', question_id=question.id, _external=True)
        if field != 'rand_id':
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
@app.route('/tossup/<int:question_id>')
def tossup(question_id=-1):
    if question_id > 0:
        question = Question.query.get(question_id)
        if question not in filter(params=[]):
            return redirect(url_for('tossup'))
    else:
        questions = filter().all()
        # reset settings if they filter out all questions, for example if the source does not contain any questions of a particular category
        if len(questions) <= 0:
            flash("The inputted settings did not match any available questions. Please try again.")
            questions = filter(params=[]).all()
            session['categories'] = []
            session['sources'] =[]
        question = random.choice(questions)
    session['question_id'] = question.id
    allowed_sources = ALL_SOURCES if current_user.is_authenticated else FREE_SOURCES
    return render_template('tossup.html', question=make_public(question, html=True), settings=session, sources=allowed_sources, categories=ALL_CATEGORIES)

@app.route('/bonus')
def bonus():
    if 'question_id' in session:
        question = Question.query.get(session['question_id'])
        if question not in filter(params=[]):
            session['question_id'] = None
            return redirect(url_for('bonus'))
    else:
        questions = filter().all()
        if len(questions) <= 0:
            flash("The inputted settings did not match any available questions. Please try again.")
            questions = filter(params=[]).all()
            session['categories'] = []
            session['sources'] = []
        question = random.choice(questions)
    allowed_sources = ALL_SOURCES if current_user.is_authenticated else FREE_SOURCES
    return render_template('bonus.html', question=make_public(question, html=True), settings=session, sources=allowed_sources, categories=ALL_CATEGORIES)

@app.route('/browse')
@app.route('/browse/<int:page>')
def browse(page=1):
    questions = filter().order_by(Question.rand_id)
    if 'search' in session and session['search'] is not None and len(session['search']) > 0:
        questions = questions.whoosh_search(session['search'])
    questions = questions.paginate(page, app.config['QUESTIONS_PER_PAGE'], False)
    if len(questions.items) <= 0:
        flash("The inputted settings did not match any available questions. Please try again.")
        questions=filter(params=[]).order_by(Question.rand_id).paginate(page, QUESTIONS_PER_PAGE, False)
        session['categories'] = []
        session['sources'] = []
        session['search'] = ''
    sources = ALL_SOURCES if current_user.is_authenticated else FREE_SOURCES
    return render_template('browse.html', questions=[make_public(question, html=True) for question in questions.items], pagination=questions, settings=session, sources=sources, categories=ALL_CATEGORIES)

@app.route('/round')
@app.route('/round/<lst>')
def round(lst=[]):
    if len(lst) >= 1:
        lst = ast.literal_eval(lst) 
        questions = [Question.query.get(i) for i in lst if i > 0 and Question.query.get(i) in filter(params=[])]
    else:
        questions = filter().order_by(func.random()).limit(25).all()
    if len(questions) <= 0:
        flash("The inputted settings did not match any available questions. Please try again.")
        questions=filter(params=[]).order_by(func.random()).limit(25).all()
        session['categories'] = []
        session['sources'] = []
    sources = ALL_SOURCES if current_user.is_authenticated else FREE_SOURCES
    return render_template('round.html', questions=[make_public(question, html=True) for question in questions], ids=[question.id for question in questions], settings=session, sources=sources, categories=ALL_CATEGORIES)

@app.route('/about')
def about():
    sources = ALL_SOURCES if current_user.is_authenticated else FREE_SOURCES
    return render_template('about.html', settings=session, num_questions=len(list(filter(params=[])))*2, sources=sources, categories=ALL_CATEGORIES) # counting both tossup and bonuses

@app.route('/settings', methods=['POST'])
def settings():
    session['categories'] = request.form.getlist('category')
    session['sources'] = request.form.getlist('source')

    next = request.args.get('next')
    if not is_safe_url(next):
        return flask.abort(400)
    else:
        return redirect(next or url_for('tossup'))

@app.route('/search', methods=['POST'])
def search():
    session['search'] = request.form.get('search')
    return redirect(url_for('browse'))

def filter(params=session, attemptAuth=True):#params=session):
    # filter questions by category and source
    questions = Question.query
    if not attemptAuth or not current_user.is_authenticated:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in FREE_SOURCES]))
    if 'categories' in params and params['categories'] is not None and len(params['categories']) > 0:
        questions = questions.filter(Question.category.in_(params['categories']))
    if 'sources' in params and params['sources'] is not None and len(params['sources']) > 0:
        questions = questions.filter(or_(*[Question.source.startswith(source) for source in params['sources']]))
    return questions

@app.route('/report', methods=['POST'])
@limiter.limit("25/day;3/minute")
def report():
    question_report(request.form.get('id'), request.form.get('message'))
    flash("Thank you for reporting a question in need of improvement!")
    
    next = request.args.get('next')
    if not is_safe_url(next):
        return flask.abort(400)
    else:
        return redirect(next or url_for('tossup'))

def question_report(id, message):
    r = requests.post(
        "https://api.mailgun.net/v3/%s/messages" % app.config['MAILGUN_DOMAIN'],
        auth=("api", app.config['MAILGUN_KEY']),
        data={
            "from": "Scibowldb User <mailgun@{}>".format(app.config['MAILGUN_DOMAIN']),
            "to": app.config['ADMINS'][0],
            "subject": "Question {} on scibowldb reported".format(id),
            "text": "Question {} was reported with the following message:\n{}".format(id,message)
        }
     )
    return r

@app.route('/login', methods=['POST'])
@limiter.limit("10/day;3/minute")
def login():
    user = User() if request.form.get('username') == app.config['LOGIN_USERNAME'] and request.form.get('password') == app.config['LOGIN_PASSWORD'] else None
    if user is not None:
        login_user(user)
        flash("Login successful!")
    else:
        flash("Invalid username and/or password")

    next = request.args.get('next')
    if not is_safe_url(next):
        return flask.abort(400)
    else:
        return redirect(next or url_for('tossup'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You logged out")
    next = request.args.get('next')
    if not is_safe_url(next):
        return flask.abort(400)
    else:
        return redirect(next or url_for('tossup'))
