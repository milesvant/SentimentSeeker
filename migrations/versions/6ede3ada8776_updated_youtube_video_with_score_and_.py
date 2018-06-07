"""Updated Youtube Video with score and default vals

Revision ID: 6ede3ada8776
Revises: 7bb34d2bec5c
Create Date: 2018-06-06 16:21:33.457895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ede3ada8776'
down_revision = '7bb34d2bec5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('youtube_videoDB', sa.Column('score', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('youtube_videoDB', 'score')
    # ### end Alembic commands ###