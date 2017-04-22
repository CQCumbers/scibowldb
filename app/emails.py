from flask_mail import Message
from app import mail, app
from config import ADMINS
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    send_async_email(app, msg)

def question_report(id, message):
    send_email('Question %s reported on scibowldb' % str(id),
        ADMINS[0],
        ADMINS,
        'Question %s was reported on scibowldb, with the following comment: %s' % (str(id), message))
