"""add_push_token_motoristas

Revision ID: add_push_token_motoristas
Revises: 425a75d6ae6d
Create Date: 2026-05-21 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_push_token_motoristas'
down_revision: Union[str, Sequence[str], None] = '425a75d6ae6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add push_token column to motoristas."""
    with op.batch_alter_table('motoristas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('push_token', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema: remove push_token column from motoristas."""
    with op.batch_alter_table('motoristas', schema=None) as batch_op:
        batch_op.drop_column('push_token')
