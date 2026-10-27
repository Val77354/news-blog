"""Small helpers shared by the posts and podcasts routers."""

from fastapi import HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import Base

# Query parameters used by every list endpoint.
SearchText = Query(None, max_length=100, description="Search text")
Limit = Query(100, ge=1, le=100, description="How many items to return (max 100)")
Offset = Query(0, ge=0, description="How many items to skip")


def get_or_404(db: Session, model: type[Base], item_id: int, label: str):
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{label} not found")
    return item


def like_pattern(text: str) -> str:
    """Turn search text into a LIKE pattern, treating % and _ as normal characters."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"
