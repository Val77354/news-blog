"""Request and response shapes.

Input models (…In) are strict: trimmed text, length limits, fixed choices,
and only safe URLs. Output models (…Out) just describe what we send back.
"""

import re
from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints

from .constants import Category, Country, PodcastSource

# A file we stored ourselves: /uploads/<uuid>.<ext>
LOCAL_UPLOAD_RE = re.compile(r"^/uploads/[0-9a-f-]{36}\.(jpg|png|webp|gif)$")
WEB_URL_RE = re.compile(r"^https?://[^\s/$.?#][^\s<>\"']*$", re.IGNORECASE)


def _web_url(value: str) -> str:
    # Blocks javascript:, data: and other schemes that could run code in a link.
    if not WEB_URL_RE.match(value):
        raise ValueError("must be a full http:// or https:// link")
    return value


def _image_url(value: str) -> str:
    if LOCAL_UPLOAD_RE.match(value):
        return value
    return _web_url(value)


def _empty_to_none(value):
    return None if isinstance(value, str) and not value.strip() else value


def Text(min_len: int, max_len: int):
    return Annotated[str, StringConstraints(strip_whitespace=True, min_length=min_len, max_length=max_len)]


# Names: letters (any language), with spaces, dots, apostrophes and hyphens
# between them. No digits or symbols: "Dr. Anna O'Neil-Smith" is fine, "4nna_99" is not.
NAME_RE = re.compile(r"^[^\W\d_]+(?:[ .'’-]+[^\W\d_]+)*\.?$")
# Control characters (invisible bytes) have no place in normal text.
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
LETTER_RE = re.compile(r"[^\W\d_]")


def _name(value: str) -> str:
    if not NAME_RE.match(value):
        raise ValueError("can only contain letters, spaces, and . ' - (no numbers or symbols)")
    return value


def _readable(min_letters: int, single_line: bool):
    def check(value: str) -> str:
        if CONTROL_CHARS_RE.search(value):
            raise ValueError("contains invisible control characters")
        if single_line and ("\n" in value or "\r" in value):
            raise ValueError("must be a single line")
        if len(LETTER_RE.findall(value)) < min_letters:
            raise ValueError(f"must contain at least {min_letters} letters, not just numbers or symbols")
        return value

    return AfterValidator(check)


Name = Annotated[Text(2, 100), AfterValidator(_name)]
Headline = Annotated[Text(3, 200), _readable(3, single_line=True)]


def Body(min_len: int, max_len: int):
    return Annotated[Text(min_len, max_len), _readable(5, single_line=False)]


WebUrl = Annotated[Text(1, 500), AfterValidator(_web_url)]
OptionalWebUrl = Annotated[WebUrl | None, BeforeValidator(_empty_to_none)]
ImageUrl = Annotated[Text(1, 500), AfterValidator(_image_url)]
# An empty field from the form means "no image".
OptionalImageUrl = Annotated[ImageUrl | None, BeforeValidator(_empty_to_none)]


def _as_utc(value: datetime) -> datetime:
    # SQLite drops the timezone; every time we store is UTC, so label it.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


UtcDatetime = Annotated[datetime, AfterValidator(_as_utc)]


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Posts ----------

PostStatus = Literal["draft", "published"]


class PostIn(StrictInput):
    title: Headline
    content: Body(10, 50_000)
    author: Name
    category: Category
    country: Country
    image_url: OptionalImageUrl = None
    status: PostStatus = "published"
    # Where an imported story came from (shown as "Read the original")
    source_url: OptionalWebUrl = None


class PostOut(ReadModel):
    id: int
    slug: str
    title: str
    content: str
    author: str
    category: str
    country: str
    image_url: str | None
    source_url: str | None
    status: str
    published_at: UtcDatetime | None
    view_count: int
    created_at: UtcDatetime
    updated_at: UtcDatetime


class ViewCount(BaseModel):
    view_count: int


# ---------- Podcasts ----------

class PodcastIn(StrictInput):
    title: Headline
    host: Name
    description: Body(10, 5_000)
    cover_image_url: OptionalImageUrl = None
    source: PodcastSource
    external_url: WebUrl


class PodcastOut(ReadModel):
    id: int
    title: str
    host: str
    description: str
    cover_image_url: str | None
    source: str
    external_url: str
    created_at: UtcDatetime


# ---------- Auth & uploads ----------

class LoginIn(StrictInput):
    password: str = Field(min_length=1, max_length=200)


class AuthStatus(BaseModel):
    admin: bool


class UploadOut(BaseModel):
    url: str
