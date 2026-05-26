"""add conversations table

Revision ID: a1b2c3d4e5f6
Revises: 8bb5d1c06e8d
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8bb5d1c06e8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('conversation_id'),
    )

    op.add_column('requests', sa.Column('conversation_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_requests_conversation_id',
        'requests', 'conversations',
        ['conversation_id'], ['conversation_id'],
        ondelete='CASCADE',
    )

    # Backfill: each existing request gets its own conversation (reuse request_id as UUID).
    op.execute("""
        INSERT INTO conversations (conversation_id, title, created_at, updated_at)
        SELECT request_id, LEFT(text, 100), created_at, created_at
        FROM requests
    """)
    op.execute("UPDATE requests SET conversation_id = request_id")


def downgrade() -> None:
    op.drop_constraint('fk_requests_conversation_id', 'requests', type_='foreignkey')
    op.drop_column('requests', 'conversation_id')
    op.drop_table('conversations')
