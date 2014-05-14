"""empty message

Revision ID: 61eea8678f
Revises: 2f8215174b
Create Date: 2014-05-06 10:48:45.024249

"""

# revision identifiers, used by Alembic.
revision = '61eea8678f'
down_revision = '2f8215174b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rasmusmediaweb_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.Unicode(length=40), nullable=True),
    sa.Column('value', sa.Unicode(length=40), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rasmusmediaweb_settings')
    ### end Alembic commands ###