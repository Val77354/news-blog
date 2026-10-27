"""Import news from the feeds listed in import_feeds.json.

    python import_news.py                  import new stories (scheduled 4x a day)
    python import_news.py --review-backlog also judge imported drafts that were
                                           never checked by the auto-publisher

Copy import_feeds.example.json to import_feeds.json and edit it. Stories are
saved as drafts. For feeds with "auto_publish": true, the good ones are then
published automatically (see app/auto_publish.py for the rules), at most
"publish_limit" per feed per run. Every run is recorded in import_news.log.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.auto_publish import DEFAULT_LIMIT, Verdict, review, unchecked_imported_drafts  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.migrations import run_migrations  # noqa: E402
from app.news_import import FeedError, import_feed  # noqa: E402

FEEDS_FILE = Path(__file__).resolve().parent / "import_feeds.json"
LOG_FILE = Path(__file__).resolve().parent / "import_news.log"


def report(line: str) -> None:
    """Print, and keep a record in import_news.log (scheduled runs have no window)."""
    stamped = f"{datetime.now():%Y-%m-%d %H:%M}  {line}"
    print(stamped)
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(stamped + "\n")


def report_verdicts(verdicts: list[Verdict]) -> None:
    for v in verdicts:
        mark = "  + published" if v.published else f"  - kept as draft ({v.reason})"
        report(f"{mark}: {v.post.title[:90]}")


def import_all(db, feeds: list[dict]) -> int:
    failures = 0
    for feed in feeds:
        try:
            result = import_feed(db, feed["url"], feed["category"], feed["country"], feed.get("limit", 10))
            report(f"{result.feed_title}: {len(result.created)} new drafts, "
                   f"{result.already_imported} already imported, {len(result.skipped)} skipped")
            if feed.get("auto_publish") and result.created:
                report_verdicts(review(db, result.created, feed.get("publish_limit", DEFAULT_LIMIT)))
        except FeedError as exc:
            failures += 1
            report(f"FAILED {feed['url']}: {exc}")
        except Exception as exc:  # one broken feed must not stop the others
            db.rollback()
            failures += 1
            report(f"FAILED {feed['url']}: unexpected {type(exc).__name__}: {exc}")
    return failures


def review_backlog(db) -> None:
    """Judge older imported drafts, grouped like feeds (same site + category)."""
    groups = defaultdict(list)
    for post in unchecked_imported_drafts(db):
        groups[(urlparse(post.source_url).hostname, post.category)].append(post)
    report(f"Reviewing {sum(len(g) for g in groups.values())} older imported drafts")
    for drafts in groups.values():
        report_verdicts(review(db, drafts, DEFAULT_LIMIT))


def main() -> None:
    if not FEEDS_FILE.exists():
        report(f"No {FEEDS_FILE.name} yet. Copy import_feeds.example.json to {FEEDS_FILE.name} and edit it.")
        sys.exit(1)
    feeds = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
    run_migrations()

    with SessionLocal() as db:
        if "--review-backlog" in sys.argv:
            review_backlog(db)
        failures = import_all(db, feeds)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
