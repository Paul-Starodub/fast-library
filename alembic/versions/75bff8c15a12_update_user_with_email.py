"""update user with email

Revision ID: 75bff8c15a12
Revises: 39586ab511f1
Create Date: 2026-02-05 22:43:12.276130

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "75bff8c15a12"
down_revision: Union[str, Sequence[str], None] = "39586ab511f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("authors", sa.Column("email", sa.String(50), nullable=True))

    op.execute("UPDATE authors SET email = 'unknown_' || id || '@example.com'")

    op.alter_column("authors", "email", nullable=False)

    op.create_unique_constraint("uq_authors_email", "authors", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_authors_email", "authors", type_="unique")
    op.drop_column("authors", "email")
