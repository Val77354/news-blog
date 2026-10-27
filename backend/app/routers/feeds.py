"""RSS feed (for feed readers) and sitemap (for search engines)."""

from email.utils import format_datetime
from datetime import timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Post

router = APIRouter(tags=["feeds"])

FEED_SIZE = 30


def _published(db: Session, limit: int | None = None) -> list[Post]:
    query = (
        select(Post)
        .where(Post.status == "published")
        .order_by(func.coalesce(Post.published_at, Post.created_at).desc(), Post.id.desc())
    )
    return db.scalars(query.limit(limit) if limit else query).all()


def _post_url(post: Post) -> str:
    return f"{settings.site_url}/posts/{post.slug}"


def _utc(dt):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _xml(body: str, media_type: str) -> Response:
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?>\n{body}',
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=600"},
    )


@router.get("/feed.xml")
def rss_feed(db: Session = Depends(get_db)):
    items = []
    for post in _published(db, FEED_SIZE):
        summary = post.content[:300] + ("…" if len(post.content) > 300 else "")
        items.append(f"""    <item>
      <title>{escape(post.title)}</title>
      <link>{escape(_post_url(post))}</link>
      <guid isPermaLink="true">{escape(_post_url(post))}</guid>
      <pubDate>{format_datetime(_utc(post.published_at or post.created_at))}</pubDate>
      <author>{escape(post.author)}</author>
      <category>{escape(post.category)}</category>
      <description>{escape(summary)}</description>
    </item>""")
    body = f"""<rss version="2.0">
  <channel>
    <title>The Daily Current</title>
    <link>{escape(settings.site_url)}</link>
    <description>Independent reporting on technology, business, science, and the world.</description>
{chr(10).join(items)}
  </channel>
</rss>"""
    return _xml(body, "application/rss+xml")


@router.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    urls = [f"  <url><loc>{escape(settings.site_url)}/</loc></url>",
            f"  <url><loc>{escape(settings.site_url)}/podcasts</loc></url>"]
    for post in _published(db):
        lastmod = _utc(post.updated_at).date().isoformat()
        urls.append(f"  <url><loc>{escape(_post_url(post))}</loc><lastmod>{lastmod}</lastmod></url>")
    body = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>"
    return _xml(body, "application/xml")
