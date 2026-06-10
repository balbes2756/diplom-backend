"""добавлено поле is_active для petsLost

Revision ID: 96374d419127
Revises: 40d10d62c7a2
Create Date: 2026-06-08 19:57:52.482849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96374d419127'
down_revision: Union[str, Sequence[str], None] = '40d10d62c7a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'petsLost',
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'))
    )


def downgrade() -> None:
    op.drop_column('petsLost', 'is_active')
