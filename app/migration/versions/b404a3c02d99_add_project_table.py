"""Add project table

Revision ID: b404a3c02d99
Revises: d8ee439a54d8
Create Date: 2025-02-10 15:19:16.784949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b404a3c02d99'
down_revision: Union[str, None] = 'd8ee439a54d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('projects',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description_small', sa.String(), nullable=True),
    sa.Column('description_large', sa.String(), nullable=True),
    sa.Column('telegram_bot_url', sa.String(), nullable=True),
    sa.Column('developers', sa.String(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('github_link', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )


def downgrade() -> None:
    op.drop_table('projects')
