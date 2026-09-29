from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


@router.get("", response_model=list[schemas.PodcastOut])
def list_podcasts(db: Session = Depends(get_db)):
    return db.query(models.Podcast).order_by(models.Podcast.created_at.desc()).all()


@router.get("/{podcast_id}", response_model=schemas.PodcastOut)
def get_podcast(podcast_id: int, db: Session = Depends(get_db)):
    podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if podcast is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")
    return podcast


@router.post("", response_model=schemas.PodcastOut, status_code=status.HTTP_201_CREATED)
def create_podcast(podcast: schemas.PodcastCreate, db: Session = Depends(get_db)):
    db_podcast = models.Podcast(**podcast.model_dump())
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast


@router.put("/{podcast_id}", response_model=schemas.PodcastOut)
def update_podcast(podcast_id: int, podcast: schemas.PodcastUpdate, db: Session = Depends(get_db)):
    db_podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if db_podcast is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")
    for field, value in podcast.model_dump().items():
        setattr(db_podcast, field, value)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast


@router.delete("/{podcast_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_podcast(podcast_id: int, db: Session = Depends(get_db)):
    db_podcast = db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()
    if db_podcast is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Podcast not found")
    db.delete(db_podcast)
    db.commit()
    return None
