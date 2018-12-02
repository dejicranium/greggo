"""migrate user table

Revision ID: 97ef2e33e45c
Revises: 
Create Date: 2018-07-07 17:42:05.517677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97ef2e33e45c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('polls_voted_in', sa.relationship(), backref='polls_voted_in', primaryjoin=id==Vote.id))

def downgrade():
    pass
