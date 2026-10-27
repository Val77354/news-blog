"""Saving and deleting uploaded images.

Every upload is opened with Pillow and saved again as a fresh WebP file.
This throws away anything hidden in the original (GPS location, camera data,
scripts disguised as images) and rejects files that aren't real images.
"""

import io
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .config import log, settings
from .schemas import LOCAL_UPLOAD_RE

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
MAX_PIXELS = 40_000_000  # about 8000 x 5000; stops "decompression bomb" files
MAX_SIDE = 2400  # big enough for any screen, keeps files small
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def _reject(message: str) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, message)


async def _read_limited(file: UploadFile) -> bytes:
    data = await file.read(settings.max_upload_bytes + 1)
    if not data:
        raise _reject("Uploaded file is empty.")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image must be smaller than 5MB.")
    return data


async def save_upload(file: UploadFile) -> str:
    """Check, clean and store an uploaded image. Returns its /uploads/... URL."""
    data = await _read_limited(file)
    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.format not in ALLOWED_FORMATS:
                raise _reject("Only JPEG, PNG, WEBP, or GIF images are allowed.")
            img.load()
            img = ImageOps.exif_transpose(img)  # keep phone photos the right way up
            img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")
            img.thumbnail((MAX_SIDE, MAX_SIDE))
            out = io.BytesIO()
            img.save(out, "WEBP", quality=85)  # no exif= argument, so metadata is dropped
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError):
        raise _reject("That file is not a valid image.")

    filename = f"{uuid.uuid4()}.webp"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    (settings.upload_dir / filename).write_bytes(out.getvalue())
    return f"/uploads/{filename}"


def _is_still_used(db: Session, url: str) -> bool:
    post_hit = db.scalar(select(models.Post.id).where(models.Post.image_url == url).limit(1))
    podcast_hit = db.scalar(select(models.Podcast.id).where(models.Podcast.cover_image_url == url).limit(1))
    return post_hit is not None or podcast_hit is not None


def delete_if_unused(db: Session, url: str | None) -> None:
    """Delete a stored upload, but only if it's ours and nothing uses it anymore.

    Call this AFTER the database commit, so a failed save never loses an image.
    """
    if not url or not LOCAL_UPLOAD_RE.match(url) or _is_still_used(db, url):
        return
    path: Path = settings.upload_dir / url.removeprefix("/uploads/")
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        log.warning("Could not delete %s: %s", path, exc)


def check_image_source(new_url: str | None, current_url: str | None = None) -> None:
    """New images must be uploaded here. Links to other sites let those sites
    see every reader's IP address, so they're only kept on posts that had them
    before this rule existed (and only while unchanged)."""
    if new_url and not LOCAL_UPLOAD_RE.match(new_url) and new_url != current_url:
        raise _reject("Please upload the image instead of linking to another website.")
