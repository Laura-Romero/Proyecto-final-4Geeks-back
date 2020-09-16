"""empty message

Revision ID: f0ce150c5d84
Revises: 
Create Date: 2020-09-15 20:24:46.691055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0ce150c5d84'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=25), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.Column('fullname', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('gender', sa.String(length=30), nullable=True),
    sa.Column('twitter', sa.String(length=30), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('twitter'),
    sa.UniqueConstraint('username')
    )
    op.create_table('user_o_auth',
    sa.Column('id', sa.String(length=767), nullable=False),
    sa.Column('email', sa.String(length=767), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('profile_pic', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('widget',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('widget_type', sa.Enum('Twitter', 'Gmail', 'Tasks', 'Weather', 'Clock', 'Compliments'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('widget_type')
    )
    op.create_table('widget_property',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('widget_property', sa.String(length=250), nullable=False),
    sa.Column('property_value', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('association',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('widget_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['widget_id'], ['widget.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association')
    op.drop_table('widget_property')
    op.drop_table('widget')
    op.drop_table('user_o_auth')
    op.drop_table('user')
    # ### end Alembic commands ###