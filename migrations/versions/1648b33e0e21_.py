"""empty message

Revision ID: 1648b33e0e21
Revises: 
Create Date: 2017-04-22 19:15:18.831047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1648b33e0e21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_question_bonus_format'), 'question', ['bonus_format'], unique=False)
    op.create_index(op.f('ix_question_category'), 'question', ['category'], unique=False)
    op.create_index(op.f('ix_question_source'), 'question', ['source'], unique=False)
    op.create_index(op.f('ix_question_tossup_format'), 'question', ['tossup_format'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_question_tossup_format'), table_name='question')
    op.drop_index(op.f('ix_question_source'), table_name='question')
    op.drop_index(op.f('ix_question_category'), table_name='question')
    op.drop_index(op.f('ix_question_bonus_format'), table_name='question')
    # ### end Alembic commands ###