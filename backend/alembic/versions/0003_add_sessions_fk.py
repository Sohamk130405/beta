"""add sessions user fk

Revision ID: 0003_add_sessions_fk
Revises: 0002_add_sessions_table
Create Date: 2026-08-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_sessions_fk"
down_revision = "0002_add_sessions_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # create a foreign key constraint from sessions.user_id -> users.id
    op.create_foreign_key(
        "fk_sessions_user_id_users",
        "sessions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_sessions_user_id_users", "sessions", type_="foreignkey")
