import random, requests, sqlalchemy_searchable
from flask import abort, request, url_for, render_template, session, redirect, flash
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse, urljoin
from sqlalchemy.sql.expression import func

from app import app, limiter
from .api import filter_questions, make_public
from .models import Question, User, all_sources, all_categories, free_sources


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/')
@app.route('/tossup')
@app.route('/tossup/<int:question_id>')
def tossup(question_id=None):
    if question_id:
        question = Question.query.get(question_id)
        if question not in filter_questions({}):
            return redirect(url_for('tossup'))
    else:
        questions = filter_questions(session).all()
        # reset settings if they match no questions
        if len(questions) <= 0:
            flash('The inputted settings did not match any available questions. Please try again.')
            session['categories'], session['sources'] = [], []
            questions = filter_questions({}).all()
        question = random.choice(questions)

    session['question_id'] = question.id
    sources = all_sources if current_user.is_authenticated else free_sources
    return render_template(
        'tossup.html', settings=session, sources=sources,
        categories=all_categories, question=make_public(question, html=True)
    )


@app.route('/bonus')
def bonus():
    if 'question_id' in session:
        question = Question.query.get(session['question_id'])
        if question not in filter_questions({}):
            session['question_id'] = None
            return redirect(url_for('bonus'))
    else:
        questions = filter_questions(session).all()
        if len(questions) <= 0:
            flash('The inputted settings did not match any available questions. Please try again.')
            session['categories'], session['sources'] = [], []
            questions = filter_questions({}).all()
        question = random.choice(questions)

    sources = all_sources if current_user.is_authenticated else free_sources
    return render_template(
        'bonus.html', settings=session, sources=sources,
        categories=all_categories, question=make_public(question, html=True)
    )


@app.route('/browse')
@app.route('/browse/<int:page>')
def browse(page=1):
    questions = filter_questions(session).order_by(Question.id)
    if session.get('search'):
        questions = sqlalchemy_searchable.search(questions, session['search'], sort=True)
    questions = questions.paginate(page, app.config['QUESTIONS_PER_PAGE'], False)
    if len(questions.items) <= 0:
        flash('The inputted settings did not match any available questions. Please try again.')
        session['categories'], session['sources'] = [], []
        session['search'] = ''
        questions=filter_questions({}).order_by(Question.id).paginate(page, app.config['QUESTIONS_PER_PAGE'], False)

    sources = all_sources if current_user.is_authenticated else free_sources
    return render_template(
        'browse.html', settings=session, sources=sources,
        categories=all_categories, pagination=questions,
        questions=[make_public(question, html=True) for question in questions.items]
    )


@app.route('/round')
def round():
    questions = filter_questions(session).order_by(func.random()).limit(25).all()
    if len(questions) <= 0:
        flash('The inputted settings did not match any available questions. Please try again.')
        session['categories'], session['sources'] = [], []
        questions=filter_questions({}).order_by(func.random()).limit(25).all()
    sources = all_sources if current_user.is_authenticated else free_sources

    return render_template(
        'round.html', settings=session, sources=sources, categories=all_categories,
        questions=[make_public(question, html=True) for question in questions],
        ids=[question.id for question in questions]
    )


@app.route('/about')
def about():
    sources = all_sources if current_user.is_authenticated else free_sources
    # counting both tossup and bonuses
    return render_template(
        'about.html', settings=session, sources=sources, categories=all_categories,
        num_questions=len(list(filter_questions({})))
    )


@app.route('/settings', methods=['POST'])
def settings():
    session['categories'] = request.form.getlist('category')
    session['sources'] = request.form.getlist('source')

    next_url = request.args.get('next_url')
    return redirect(next_url) if is_safe_url(next_url) else redirect(url_for('tossup'))


@app.route('/search', methods=['POST'])
def search():
    session['search'] = request.form.get('search')
    return redirect(url_for('browse'))


@app.route('/report', methods=['POST'])
@limiter.limit('25/day; 3/minute')
def report():
    question_report(request.form.get('id'), request.form.get('message'))
    flash('Thank you for reporting a question in need of improvement!')
    
    next_url = request.args.get('next_url')
    return redirect(next_url) if is_safe_url(next_url) else redirect(url_for('tossup'))


def question_report(id, message):
    return requests.post(
        'https://api.mailgun.net/v3/scibowldb.com/messages',
        auth=('api', app.config['MAILGUN_KEY']),
        data={
            'from': 'ScibowlDB User <mail@scibowldb.com>',
            'to': app.config['ADMIN_EMAIL'],
            'subject': 'Question {} on scibowldb reported'.format(id),
            'text': 'Question {} was reported with the following message:\n{}'.format(id, message)
        }
    )


@app.route('/login', methods=['POST'])
@limiter.limit('10/day; 3/minute')
def login():
    username, password = request.form.get('username'), request.form.get('password')
    if username == app.config['LOGIN_USERNAME'] and password == app.config['LOGIN_PASSWORD']:
        login_user(User())
        flash('Login successful!')
    else:
        flash('Invalid username and/or password')

    next_url = request.args.get('next_url')
    return redirect(next_url or url_for('tossup')) if is_safe_url(next_url) else abort(400)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You logged out')
    next_url = request.args.get('next_url')
    return redirect(next_url or url_for('tossup')) if is_safe_url(next_url) else abort(400)
