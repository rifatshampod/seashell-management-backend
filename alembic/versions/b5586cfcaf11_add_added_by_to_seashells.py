"""add_added_by_to_seashells

Revision ID: b5586cfcaf11
Revises: 4216b852d562
Create Date: 2026-02-09 18:39:04.816070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5586cfcaf11'
down_revision: Union[str, Sequence[str], None] = '4216b852d562'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('seashells', sa.Column('added_by_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_seashells_added_by_id', 'seashells', 'users', ['added_by_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_seashells_added_by_id', 'seashells', type_='foreignkey')
    op.drop_column('seashells', 'added_by_id')

