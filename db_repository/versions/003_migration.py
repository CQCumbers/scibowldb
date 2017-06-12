from sqlalchemy import Table, MetaData, String, Column


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    question = Table('question', meta, autoload=True)
    reported = question.c.reported
    reported.drop()

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    question = Table('question', meta, autoload=True)
    reported = Column('reported', Boolean)
    reported.create(question)
