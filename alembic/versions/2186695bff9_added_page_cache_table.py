"""Added page_cache table

Revision ID: 2186695bff9
Revises: 61eea8678f
Create Date: 2014-05-12 19:31:28.061758

"""

# revision identifiers, used by Alembic.
revision = '2186695bff9'
down_revision = '61eea8678f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rasmusmediaweb_path_cache',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.Unicode(length=255), nullable=True),
    sa.Column('data', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('path')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rasmusmediaweb_path_cache')
    ### end Alembic commands ###
