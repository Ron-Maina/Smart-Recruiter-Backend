"""Test

Revision ID: df9d3d891113
Revises: e0d335df4c89
Create Date: 2023-11-01 00:26:14.450016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df9d3d891113'
down_revision = 'e0d335df4c89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('whiteboard', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bdd', sa.String(length=500), nullable=False))
        batch_op.add_column(sa.Column('pseudocode', sa.String(length=500), nullable=False))
        batch_op.add_column(sa.Column('code', sa.String(length=500), nullable=False))
        batch_op.add_column(sa.Column('grade', sa.Integer(), nullable=True))
        batch_op.drop_column('bdd_text')
        batch_op.drop_column('code_text')
        batch_op.drop_column('pseudocode_text')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('whiteboard', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pseudocode_text', sa.VARCHAR(length=500), nullable=False))
        batch_op.add_column(sa.Column('code_text', sa.VARCHAR(length=500), nullable=False))
        batch_op.add_column(sa.Column('bdd_text', sa.VARCHAR(length=500), nullable=False))
        batch_op.drop_column('grade')
        batch_op.drop_column('code')
        batch_op.drop_column('pseudocode')
        batch_op.drop_column('bdd')

    # ### end Alembic commands ###
