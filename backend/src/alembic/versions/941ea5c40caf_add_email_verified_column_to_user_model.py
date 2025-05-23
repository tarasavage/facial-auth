"""Add email verified column to User model

Revision ID: 941ea5c40caf
Revises: 2b4948bb2f1c
Create Date: 2025-03-06 22:20:12.485219

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "941ea5c40caf"
down_revision: Union[str, None] = "2b4948bb2f1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), server_default="false", nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "email_verified")
    # ### end Alembic commands ###
