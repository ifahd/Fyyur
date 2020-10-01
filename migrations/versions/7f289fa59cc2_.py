"""empty message

Revision ID: 7f289fa59cc2
Revises: aced77a5fced
Create Date: 2020-10-01 19:33:15.621988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f289fa59cc2'
down_revision = 'aced77a5fced'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('available_from_date', sa.DateTime(), nullable=True))
    op.add_column('artists', sa.Column('available_to_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'available_to_date')
    op.drop_column('artists', 'available_from_date')
    # ### end Alembic commands ###