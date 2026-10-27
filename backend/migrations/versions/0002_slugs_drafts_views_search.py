"""Add slugs, draft/published status, real view counts, and full-text search.

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
from alembic import op

from app.slugs import unique_slug

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("posts") as batch:
        batch.add_column(sa.Column("slug", sa.String(100), nullable=True))
        batch.add_column(sa.Column("status", sa.String(20), nullable=False, server_default="published"))
        batch.add_column(sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("view_count", sa.Integer, nullable=False, server_default="0"))

    conn = op.get_bind()
    # Existing posts were already public, so they count as published when created.
    conn.execute(sa.text("UPDATE posts SET published_at = created_at"))
    taken: set[str] = set()
    for post_id, title in conn.execute(sa.text("SELECT id, title FROM posts ORDER BY id")).all():
        slug = unique_slug(title, taken.__contains__)
        taken.add(slug)
        conn.execute(sa.text("UPDATE posts SET slug = :slug WHERE id = :id"), {"slug": slug, "id": post_id})
    op.create_index("ix_posts_slug", "posts", ["slug"], unique=True)

    # Full-text search index over title, content and author, kept in sync by triggers.
    op.execute("""
        CREATE VIRTUAL TABLE posts_fts USING fts5(
            title, content, author,
            content='posts', content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        )
    """)
    op.execute("""
        CREATE TRIGGER posts_fts_insert AFTER INSERT ON posts BEGIN
            INSERT INTO posts_fts(rowid, title, content, author)
            VALUES (new.id, new.title, new.content, new.author);
        END
    """)
    op.execute("""
        CREATE TRIGGER posts_fts_delete AFTER DELETE ON posts BEGIN
            INSERT INTO posts_fts(posts_fts, rowid, title, content, author)
            VALUES ('delete', old.id, old.title, old.content, old.author);
        END
    """)
    op.execute("""
        CREATE TRIGGER posts_fts_update AFTER UPDATE OF title, content, author ON posts BEGIN
            INSERT INTO posts_fts(posts_fts, rowid, title, content, author)
            VALUES ('delete', old.id, old.title, old.content, old.author);
            INSERT INTO posts_fts(rowid, title, content, author)
            VALUES (new.id, new.title, new.content, new.author);
        END
    """)
    op.execute("INSERT INTO posts_fts(posts_fts) VALUES ('rebuild')")


def downgrade() -> None:
    for trigger in ("posts_fts_insert", "posts_fts_delete", "posts_fts_update"):
        op.execute(f"DROP TRIGGER IF EXISTS {trigger}")
    op.execute("DROP TABLE IF EXISTS posts_fts")
    op.drop_index("ix_posts_slug", "posts")
    with op.batch_alter_table("posts") as batch:
        for column in ("view_count", "published_at", "status", "slug"):
            batch.drop_column(column)
