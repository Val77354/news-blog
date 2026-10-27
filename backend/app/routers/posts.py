import re
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import Select, column, func, literal_column, select, table, update
from sqlalchemy.orm import Session

from ..database import get_db
from ..images import check_image_source, delete_if_unused
from ..models import Post
from ..schemas import PostIn, PostOut, ViewCount
from ..security import is_admin, require_admin
from ..slugs import unique_slug
from .common import Limit, Offset, SearchText, get_or_404

router = APIRouter(prefix="/posts", tags=["posts"])

# The full-text search index created in migration 0002.
posts_fts = table("posts_fts", column("rowid"), column("rank"))

# Newest first: published date, or creation date for drafts.
NEWEST_FIRST = (func.coalesce(Post.published_at, Post.created_at).desc(), Post.id.desc())


def _visible_to(request: Request, query: Select) -> Select:
    """Visitors only ever see published posts; the admin also sees drafts."""
    return query if is_admin(request) else query.where(Post.status == "published")


def _full_text_match(text: str) -> str | None:
    """Turn what the visitor typed into a safe full-text query.
    Every word must appear; each word also matches longer words ("geneva" -> "genevan")."""
    words = re.findall(r"\w+", text)[:10]
    return " ".join(f'"{w}"*' for w in words) or None


@router.get("", response_model=list[PostOut])
def list_posts(
    request: Request,
    category: str | None = Query(None, max_length=50),
    countries: str | None = Query(None, max_length=500, description="Comma-separated country names"),
    q: str | None = SearchText,
    limit: int = Limit,
    offset: int = Offset,
    db: Session = Depends(get_db),
):
    query = _visible_to(request, select(Post))
    if category:
        query = query.where(Post.category == category)
    if countries:
        country_list = [c.strip() for c in countries.split(",") if c.strip()][:20]
        if country_list:
            query = query.where(Post.country.in_(country_list))

    match = _full_text_match(q) if q else None
    if q and not match:
        return []
    if match:
        # Best matches first, using SQLite's built-in full-text search (FTS5).
        query = (
            query.join(posts_fts, posts_fts.c.rowid == Post.id)
            .where(literal_column("posts_fts").op("MATCH")(match))
            .order_by(posts_fts.c.rank, *NEWEST_FIRST)
        )
    else:
        query = query.order_by(*NEWEST_FIRST)
    return db.scalars(query.limit(limit).offset(offset)).all()


@router.get("/{key}", response_model=PostOut)
def get_post(key: str, request: Request, db: Session = Depends(get_db)):
    """Find a post by its readable address (slug), or by number for old links."""
    query = select(Post).where(Post.id == int(key) if key.isdigit() else Post.slug == key)
    post = db.scalar(_visible_to(request, query))
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return post


# ---------- View counts ----------

VIEW_WINDOW_SECONDS = 30 * 60  # the same visitor counts once per post per half hour
_recent_views: dict[tuple[str, int], float] = {}


@router.post("/{post_id}/view", response_model=ViewCount)
def record_view(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = get_or_404(db, Post, post_id, "Post")
    if post.status != "published" or is_admin(request):
        return {"view_count": post.view_count}  # don't count drafts or your own visits

    now = time.time()
    visitor = (request.client.host if request.client else "unknown", post_id)
    if now - _recent_views.get(visitor, 0) > VIEW_WINDOW_SECONDS:
        if len(_recent_views) > 50_000:
            _recent_views.clear()  # keep memory use bounded
        _recent_views[visitor] = now
        # Add 1 in the database itself so simultaneous visits aren't lost,
        # and keep updated_at unchanged (a view isn't an edit).
        db.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(view_count=Post.view_count + 1, updated_at=Post.updated_at)
        )
        db.commit()
        db.refresh(post)
    return {"view_count": post.view_count}


# ---------- Admin: create, edit, delete ----------

def _apply_publish_date(post: Post) -> None:
    if post.status == "published" and post.published_at is None:
        post.published_at = datetime.now(timezone.utc)


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_post(data: PostIn, db: Session = Depends(get_db)):
    check_image_source(data.image_url)
    slug_taken = lambda slug: db.scalar(select(Post.id).where(Post.slug == slug)) is not None  # noqa: E731
    post = Post(**data.model_dump(), slug=unique_slug(data.title, slug_taken))
    _apply_publish_date(post)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostOut, dependencies=[Depends(require_admin)])
def update_post(post_id: int, data: PostIn, db: Session = Depends(get_db)):
    # The slug stays the same when the title changes, so shared links keep working.
    post = get_or_404(db, Post, post_id, "Post")
    check_image_source(data.image_url, post.image_url)
    old_image = post.image_url
    for field, value in data.model_dump().items():
        setattr(post, field, value)
    _apply_publish_date(post)
    db.commit()
    db.refresh(post)
    if old_image != post.image_url:
        delete_if_unused(db, old_image)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = get_or_404(db, Post, post_id, "Post")
    image = post.image_url
    db.delete(post)
    db.commit()
    delete_if_unused(db, image)
