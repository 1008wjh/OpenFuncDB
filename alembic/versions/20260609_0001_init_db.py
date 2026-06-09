"""init_db

Fresh database schema for OpenFuncDB v2.0.
Creates all tables from scratch.

Revision ID: 0001
Revises:
Create Date: 2026-06-09
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'func_base',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('func_type', sa.String(50), nullable=False),
        sa.Column('func_name', sa.String(200), nullable=False),
        sa.Column('func_content', sa.Text(), nullable=False),
        sa.Column('func_desc', sa.Text(), nullable=True),
        sa.Column('func_params', sa.Text(), nullable=True),
        sa.Column('func_return', sa.Text(), nullable=True),
        sa.Column('is_safe', sa.Boolean(), default=False),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_func_base_id', 'func_base', ['id'])
    op.create_index('ix_func_base_func_type', 'func_base', ['func_type'])

    op.create_table(
        'func_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('func_type', sa.String(50), nullable=True),
        sa.Column('category_desc', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_func_category_id', 'func_category', ['id'])
    op.create_index('ix_func_category_func_type', 'func_category', ['func_type'])

    op.create_table(
        'func_category_relation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('func_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['func_id'], ['func_base.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['func_category.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_func_category_relation_id', 'func_category_relation', ['id'])

    op.create_table(
        'func_audit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('func_id', sa.Integer(), nullable=False),
        sa.Column('audit_status', sa.Integer(), default=0),
        sa.Column('audit_user', sa.String(100), nullable=True),
        sa.Column('audit_time', sa.DateTime(), nullable=True),
        sa.Column('audit_remark', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['func_id'], ['func_base.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_func_audit_id', 'func_audit', ['id'])

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('auth_level', sa.String(50), default='user'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('create_time', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_func_audit_id', table_name='func_audit')
    op.drop_table('func_audit')
    op.drop_index('ix_func_category_relation_id', table_name='func_category_relation')
    op.drop_table('func_category_relation')
    op.drop_index('ix_func_category_func_type', table_name='func_category')
    op.drop_index('ix_func_category_id', table_name='func_category')
    op.drop_table('func_category')
    op.drop_index('ix_func_base_func_type', table_name='func_base')
    op.drop_index('ix_func_base_id', table_name='func_base')
    op.drop_table('func_base')
