"""initial

Revision ID: 5f1ab001d90d
Revises: 724c302be0f4
Create Date: 2024-08-19 11:00:30.744872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f1ab001d90d'
down_revision: Union[str, None] = '724c302be0f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
