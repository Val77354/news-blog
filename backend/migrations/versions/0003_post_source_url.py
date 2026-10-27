"""Add posts.source_url: the original article for stories brought in by the importer.

Revision ID: 0003
Revises: 0002
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("posts") as batch:
        batch.add_column(sa.Column("source_url", sa.String(500), nullable=True))
    # Unique, so the same story is never imported twice.
    op.create_index("ix_posts_source_url", "posts", ["source_url"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_posts_source_url", "posts")
    with op.batch_alter_table("posts") as batch:
        batch.drop_column("source_url")
