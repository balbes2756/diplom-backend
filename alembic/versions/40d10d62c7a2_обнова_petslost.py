"""обнова petsLost

Revision ID: 40d10d62c7a2
Revises: 4b8eedb794f3
Create Date: 2026-06-02 21:14:51.956482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40d10d62c7a2'
down_revision: Union[str, Sequence[str], None] = '4b8eedb794f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('petsLost', 'owner_id', new_column_name='user_id')
    op.alter_column('petsLost', 'user_id', nullable=True)
    op.add_column('petsLost', sa.Column('contact_phone', sa.String(20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('petsLost', 'contact_phone')
    op.alter_column('petsLost', 'user_id', nullable=False)
    op.alter_column('petsLost', 'user_id', new_column_name='owner_id')
