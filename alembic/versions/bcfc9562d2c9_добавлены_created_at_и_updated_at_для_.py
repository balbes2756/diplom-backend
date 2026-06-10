"""добавлены created_at и updated_at для petsLost

Revision ID: bcfc9562d2c9
Revises: 96374d419127
Create Date: 2026-06-08 20:04:54.463902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcfc9562d2c9'
down_revision: Union[str, Sequence[str], None] = '96374d419127'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'petsLost',
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.add_column(
        'petsLost',
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_column('petsLost', 'updated_at')
    op.drop_column('petsLost', 'created_at')
