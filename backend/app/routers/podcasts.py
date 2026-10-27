from fastapi import APIRouter, Depends, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..images import delete_if_unused
from ..models import Podcast
from ..schemas import PodcastIn, PodcastOut
from ..security import require_admin
from .common import Limit, Offset, SearchText, get_or_404, like_pattern

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


@router.get("", response_model=list[PodcastOut])
def list_podcasts(
    q: str | None = SearchText,
    limit: int = Limit,
    offset: int = Offset,
    db: Session = Depends(get_db),
):
    query = select(Podcast)
    if q and q.strip():
        pattern = like_pattern(q.strip())
        query = query.where(
            or_(
                Podcast.title.ilike(pattern, escape="\\"),
                Podcast.host.ilike(pattern, escape="\\"),
                Podcast.description.ilike(pattern, escape="\\"),
            )
        )
    query = query.order_by(Podcast.created_at.desc(), Podcast.id.desc()).limit(limit).offset(offset)
    return db.scalars(query).all()


@router.get("/{podcast_id}", response_model=PodcastOut)
def get_podcast(podcast_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Podcast, podcast_id, "Podcast")


@router.post("", response_model=PodcastOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_podcast(data: PodcastIn, db: Session = Depends(get_db)):
    podcast = Podcast(**data.model_dump())
    db.add(podcast)
    db.commit()
    db.refresh(podcast)
    return podcast


@router.put("/{podcast_id}", response_model=PodcastOut, dependencies=[Depends(require_admin)])
def update_podcast(podcast_id: int, data: PodcastIn, db: Session = Depends(get_db)):
    podcast = get_or_404(db, Podcast, podcast_id, "Podcast")
    old_cover = podcast.cover_image_url
    for field, value in data.model_dump().items():
        setattr(podcast, field, value)
    db.commit()
    db.refresh(podcast)
    if old_cover != podcast.cover_image_url:
        delete_if_unused(db, old_cover)
    return podcast


@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_podcast(podcast_id: int, db: Session = Depends(get_db)):
    podcast = get_or_404(db, Podcast, podcast_id, "Podcast")
    cover = podcast.cover_image_url
    db.delete(podcast)
    db.commit()
    delete_if_unused(db, cover)
