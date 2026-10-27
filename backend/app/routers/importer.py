from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..constants import Category, Country
from ..database import get_db
from ..news_import import FeedError, import_feed
from ..schemas import PostOut, StrictInput, WebUrl
from ..security import require_admin

router = APIRouter(prefix="/import", tags=["import"], dependencies=[Depends(require_admin)])


class ImportIn(StrictInput):
    feed_url: WebUrl
    category: Category
    country: Country
    limit: int = Field(10, ge=1, le=20)


class ImportOut(BaseModel):
    feed_title: str
    created: list[PostOut]
    already_imported: int
    skipped: list[str]


@router.post("", response_model=ImportOut)
def import_news(data: ImportIn, db: Session = Depends(get_db)):
    """Bring in the latest stories from an RSS/Atom feed as drafts."""
    try:
        result = import_feed(db, data.feed_url, data.category, data.country, data.limit)
    except FeedError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return {
        "feed_title": result.feed_title,
        "created": result.created,
        "already_imported": result.already_imported,
        "skipped": result.skipped,
    }
