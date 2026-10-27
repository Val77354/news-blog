"""Bring in news stories from other sites' RSS/Atom feeds.

RSS feeds are what news sites publish so others can follow their headlines,
which makes them the fair way to collect news (scraping whole web pages is
fragile and copying full articles breaks copyright). For each story we keep:
  - the headline,
  - a short summary (at most SUMMARY_CHARS characters),
  - a link to the original article (source_url).
Every imported story is saved as a DRAFT, so nothing goes public until you
have read it, edited it, and published it yourself.
"""

import html
import ipaddress
import re
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urlparse

from defusedxml import ElementTree
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import log, settings
from .models import Post
from .schemas import NAME_RE, PostIn
from .slugs import unique_slug

MAX_FEED_BYTES = 3 * 1024 * 1024
TIMEOUT_SECONDS = 10
SUMMARY_CHARS = 600
FALLBACK_AUTHOR = "News Desk"
USER_AGENT = "DailyCurrentNewsImporter/1.0 (+{site})"


class FeedError(Exception):
    """A problem worth showing to the admin (bad address, not a feed, ...)."""


# ---------- Safe downloading ----------

def _check_public_address(url: str) -> None:
    """Only fetch from public internet addresses. This stops the importer from
    being pointed at this computer or the local network (SSRF)."""
    parts = urlparse(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise FeedError("The feed address must start with http:// or https://")
    try:
        infos = socket.getaddrinfo(parts.hostname, parts.port or None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise FeedError(f"Couldn't find the website {parts.hostname}.")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise FeedError("That address points to a private network, which isn't allowed.")


class _SafeRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _check_public_address(newurl)  # a redirect must not lead somewhere private either
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_SafeRedirects)


def download_feed(url: str) -> bytes:
    _check_public_address(url)
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT.format(site=settings.site_url),
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
    })
    try:
        with _opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            data = response.read(MAX_FEED_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise FeedError(f"The website answered with an error ({exc.code}).")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FeedError(f"Couldn't download the feed: {getattr(exc, 'reason', exc)}")
    if len(data) > MAX_FEED_BYTES:
        raise FeedError("That feed is too large.")
    return data


# ---------- Reading the feed ----------

@dataclass
class FeedItem:
    title: str
    link: str
    summary: str
    author: str | None = None


@dataclass
class Feed:
    title: str
    items: list[FeedItem] = field(default_factory=list)


class _TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(raw: str | None) -> str:
    """Feed summaries often contain HTML. Keep only the readable text."""
    if not raw:
        return ""
    parser = _TextOnly()
    parser.feed(html.unescape(raw))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def shorten(text: str, limit: int = SUMMARY_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]  # drop the XML namespace: "{http://...}title" -> "title"


def _child(element, name: str):
    return next((c for c in element if _local(c.tag) == name), None)


def _text(element, *names: str) -> str:
    for name in names:
        child = _child(element, name)
        if child is not None and (child.text or "").strip():
            return child.text.strip()
    return ""


def parse_feed(data: bytes) -> Feed:
    try:
        root = ElementTree.fromstring(data)
    except Exception:  # defusedxml raises several kinds of errors for bad or hostile XML
        raise FeedError("That address doesn't contain a valid RSS or Atom feed.")

    if _local(root.tag) in ("rss", "RDF"):  # RSS 2.0, or the older RSS 1.0 ("RDF")
        channel = _child(root, "channel")
        if channel is None:
            raise FeedError("That RSS feed has no channel.")
        feed = Feed(title=_text(channel, "title"))
        # RSS 2.0 puts the stories inside <channel>; RSS 1.0 puts them next to it.
        for item in [*channel, *root]:
            if _local(item.tag) == "item":
                feed.items.append(FeedItem(
                    title=plain_text(_text(item, "title")),
                    link=_text(item, "link"),
                    summary=plain_text(_text(item, "description", "encoded")),
                    author=plain_text(_text(item, "creator", "author")) or None,
                ))
        return feed

    if _local(root.tag) == "feed":  # Atom
        feed = Feed(title=_text(root, "title"))
        for entry in root:
            if _local(entry.tag) != "entry":
                continue
            link = next((c.get("href", "") for c in entry
                         if _local(c.tag) == "link" and c.get("rel", "alternate") == "alternate"), "")
            author = _child(entry, "author")
            feed.items.append(FeedItem(
                title=plain_text(_text(entry, "title")),
                link=link,
                summary=plain_text(_text(entry, "summary", "content")),
                author=plain_text(_text(author, "name")) if author is not None else None,
            ))
        return feed

    raise FeedError("That address doesn't contain a valid RSS or Atom feed.")


# ---------- Saving stories as drafts ----------

@dataclass
class ImportResult:
    feed_title: str
    created: list[Post] = field(default_factory=list)
    already_imported: int = 0
    skipped: list[str] = field(default_factory=list)


def _pick_author(item: FeedItem, feed_title: str) -> str:
    for candidate in (item.author, feed_title):
        if candidate and 2 <= len(candidate) <= 100 and NAME_RE.match(candidate):
            return candidate
    return FALLBACK_AUTHOR


def _site_name(link: str) -> str:
    return (urlparse(link).hostname or "the original site").removeprefix("www.")


def import_feed(db: Session, feed_url: str, category: str, country: str, limit: int = 10) -> ImportResult:
    feed = parse_feed(download_feed(feed_url))
    result = ImportResult(feed_title=feed.title or _site_name(feed_url))

    for item in feed.items[:limit]:
        if not item.link or not item.title:
            result.skipped.append(item.title or "(story without a title or link)")
            continue
        if db.scalar(select(Post.id).where(Post.source_url == item.link)) is not None:
            result.already_imported += 1
            continue

        summary = shorten(item.summary) or item.title
        content = f"{summary}\n\nSource: {result.feed_title}."  # the post page links to the original
        try:
            # The same strict checks as a post you write yourself.
            data = PostIn(
                title=shorten(item.title, 200),
                content=content,
                author=_pick_author(item, feed.title),
                category=category,
                country=country,
                status="draft",
                source_url=item.link,
            )
        except ValidationError as exc:
            log.info("Skipped imported story %r: %s", item.title, exc.errors()[0]["msg"])
            result.skipped.append(item.title)
            continue

        taken = lambda slug: db.scalar(select(Post.id).where(Post.slug == slug)) is not None  # noqa: E731
        post = Post(**data.model_dump(), slug=unique_slug(data.title, taken))
        db.add(post)
        db.flush()  # gives the post its id and reserves the slug for the next story
        result.created.append(post)

    db.commit()
    log.info("Imported %d stories from %s", len(result.created), feed_url)
    return result
