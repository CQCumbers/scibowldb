from app import db

class Question(db.Model):
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
