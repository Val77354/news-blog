from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..images import delete_if_unused
from ..models import Post
from ..schemas import PostIn, PostOut
from ..security import require_admin
from .common import Limit, Offset, SearchText, get_or_404, like_pattern

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostOut])
def list_posts(
    category: str | None = Query(None, max_length=50),
    countries: str | None = Query(None, max_length=500, description="Comma-separated country names"),
    q: str | None = SearchText,
    limit: int = Limit,
    offset: int = Offset,
    db: Session = Depends(get_db),
):
    query = select(Post)
    if category:
        query = query.where(Post.category == category)
    if countries:
        country_list = [c.strip() for c in countries.split(",") if c.strip()][:20]
        if country_list:
            query = query.where(Post.country.in_(country_list))
    if q and q.strip():
        pattern = like_pattern(q.strip())
        query = query.where(
            or_(
                Post.title.ilike(pattern, escape="\\"),
                Post.content.ilike(pattern, escape="\\"),
                Post.author.ilike(pattern, escape="\\"),
            )
        )
    query = query.order_by(Post.created_at.desc(), Post.id.desc()).limit(limit).offset(offset)
    return db.scalars(query).all()


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Post, post_id, "Post")


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_post(data: PostIn, db: Session = Depends(get_db)):
    post = Post(**data.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostOut, dependencies=[Depends(require_admin)])
def update_post(post_id: int, data: PostIn, db: Session = Depends(get_db)):
    post = get_or_404(db, Post, post_id, "Post")
    old_image = post.image_url
    for field, value in data.model_dump().items():
        setattr(post, field, value)
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
