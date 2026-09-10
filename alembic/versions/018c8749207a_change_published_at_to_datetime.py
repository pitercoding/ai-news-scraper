"""change published_at to datetime

Revision ID: 018c8749207a
Revises: 4d8c4f864c4f
Create Date: 2026-09-10 16:49:32.687319

"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "018c8749207a"
down_revision: Union[str, Sequence[str], None] = "4d8c4f864c4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            ALTER TABLE articles
            ADD COLUMN published_at_new DATETIME
            """
        )
    )

    rows = connection.execute(
        sa.text(
            """
            SELECT id, published_at
            FROM articles
            """
        )
    ).fetchall()

    for row in rows:
        published_at = datetime.strptime(
            row.published_at,
            "%a, %d %b %Y %H:%M:%S %z",
        )

        published_at_utc = (
            published_at
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

        connection.execute(
            sa.text(
                """
                UPDATE articles
                SET published_at_new = :published_at
                WHERE id = :id
                """
            ),
            {
                "id": row.id,
                "published_at": published_at_utc,
            },
        )

    with op.batch_alter_table("articles") as batch_op:
        batch_op.drop_column("published_at")

    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column(
            "published_at_new",
            new_column_name="published_at",
            existing_type=sa.DateTime(),
            nullable=False,
        )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            ALTER TABLE articles
            ADD COLUMN published_at_old VARCHAR(100)
            """
        )
    )

    rows = connection.execute(
        sa.text(
            """
            SELECT id, published_at
            FROM articles
            """
        )
    ).fetchall()

    for row in rows:
        published_at = datetime.fromisoformat(
            row.published_at
        )

        published_at_formatted = published_at.strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )

        connection.execute(
            sa.text(
                """
                UPDATE articles
                SET published_at_old = :published_at
                WHERE id = :id
                """
            ),
            {
                "id": row.id,
                "published_at": published_at_formatted,
            },
        )

    with op.batch_alter_table("articles") as batch_op:
        batch_op.drop_column("published_at")

    with op.batch_alter_table("articles") as batch_op:
        batch_op.alter_column(
            "published_at_old",
            new_column_name="published_at",
            existing_type=sa.String(length=100),
            nullable=False,
        )