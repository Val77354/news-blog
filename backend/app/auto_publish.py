"""Publish the good imported drafts automatically.

Only drafts that came from the news importer (they have a source_url) are
considered. Posts you write yourself are never touched. Each imported draft is
judged exactly once, right after it arrives, so a story you unpublish later
stays unpublished.

A draft is published when:
  - it isn't a podcast, video, live blog, quiz, gallery or newsletter,
  - it has a real summary (at least MIN_SUMMARY_CHARS characters),
  - it isn't a near-duplicate of a story published in the last DUPLICATE_DAYS days,
  - fewer than `limit` stories from the same batch were published already,
    so one busy feed can't flood the home page.
Drafts that fail stay drafts. The reason is returned, for the log.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Post

MIN_SUMMARY_CHARS = 80
DUPLICATE_DAYS = 3
DEFAULT_LIMIT = 3

# Formats that don't work as a text story on this site.
NOT_AN_ARTICLE = re.compile(
    r"\b(podcast|video|watch|live|as it happened|quiz|in pictures|gallery|photos|newsletter|sign up|crossword)\b",
    re.IGNORECASE,
)
STOPWORDS = {
    "the", "and", "for", "with", "after", "from", "that", "this", "over", "into", "says", "said",
    "will", "have", "has", "new", "about", "than", "more", "most", "its", "are", "was", "his", "her",
    "how", "why", "what", "who", "wins", "win", "first",
}


@dataclass
class Verdict:
    post: Post
    published: bool
    reason: str  # why it was held back, or "published"


def _summary(post: Post) -> str:
    return post.content.split("\n\nSource:")[0].strip()


def _key_words(title: str) -> set[str]:
    words = re.findall(r"\w+", title.lower().replace("’", "").replace("'", ""))
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}


def is_near_duplicate(title: str, other: str) -> bool:
    """Same story from another site? At least 3 important words in common,
    covering at least half of the shorter headline."""
    a, b = _key_words(title), _key_words(other)
    shared = len(a & b)
    return shared >= 3 and shared / max(1, min(len(a), len(b))) >= 0.5


def problem_with(post: Post, recent_titles: list[str]) -> str | None:
    if NOT_AN_ARTICLE.search(post.title):
        return "not a text article (podcast, video, live blog, ...)"
    if len(_summary(post)) < MIN_SUMMARY_CHARS:
        return "summary too short"
    for title in recent_titles:
        if is_near_duplicate(post.title, title):
            return f"same story as '{title[:60]}'"
    return None


def _recently_published_titles(db: Session) -> list[str]:
    since = datetime.now(timezone.utc) - timedelta(days=DUPLICATE_DAYS)
    query = select(Post.title).where(Post.status == "published", Post.published_at >= since)
    return list(db.scalars(query))


def review(db: Session, drafts: list[Post], limit: int = DEFAULT_LIMIT) -> list[Verdict]:
    """Judge a batch of imported drafts (in feed order, most prominent first)."""
    now = datetime.now(timezone.utc)
    recent = _recently_published_titles(db)
    verdicts: list[Verdict] = []
    published = 0

    for post in drafts:
        if post.status != "draft" or not post.source_url or post.auto_checked_at is not None:
            continue
        post.auto_checked_at = now
        reason = problem_with(post, recent)
        if reason is None and published >= limit:
            reason = f"limit of {limit} per feed reached"
        if reason is None:
            post.status = "published"
            post.published_at = now
            published += 1
            recent.append(post.title)
            verdicts.append(Verdict(post, True, "published"))
        else:
            verdicts.append(Verdict(post, False, reason))

    db.commit()
    return verdicts


def unchecked_imported_drafts(db: Session) -> list[Post]:
    query = (
        select(Post)
        .where(Post.status == "draft", Post.source_url.is_not(None), Post.auto_checked_at.is_(None))
        .order_by(Post.id)
    )
    return list(db.scalars(query))
