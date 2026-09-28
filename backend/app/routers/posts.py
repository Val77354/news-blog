from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .uploads import UPLOAD_DIR


def _delete_image_file(image_url: str | None) -> None:
    if not image_url or image_url.startswith("http"):
        return
    name = Path(image_url).name
    if not name:
        return
    try:
        (UPLOAD_DIR / name).unlink(missing_ok=True)
    except OSError:
        pass


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[schemas.PostOut])
def list_posts(
    category: str | None = None,
    countries: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Post)
    if category:
        query = query.filter(models.Post.category == category)
    if countries:
        country_list = [c.strip() for c in countries.split(",") if c.strip()]
        if country_list:
            query = query.filter(models.Post.country.in_(country_list))
    return query.order_by(models.Post.created_at.desc()).all()


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("", response_model=schemas.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.put("/{post_id}", response_model=schemas.PostOut)
def update_post(post_id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.image_url != db_post.image_url:
        _delete_image_file(db_post.image_url)
    for field, value in post.model_dump().items():
        setattr(db_post, field, value)
    db_post.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    _delete_image_file(db_post.image_url)
    db.delete(db_post)
    db.commit()
    return None
