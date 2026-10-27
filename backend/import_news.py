"""Import news from the feeds listed in import_feeds.json, as drafts.

    python import_news.py

Copy import_feeds.example.json to import_feeds.json and edit it. Run this by
hand, or schedule it (Windows Task Scheduler / cron) to collect news
automatically. Stories are saved as drafts: review and publish them on the site.
"""

import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def main() -> None:
    if not FEEDS_FILE.exists():
        report(f"No {FEEDS_FILE.name} yet. Copy import_feeds.example.json to {FEEDS_FILE.name} and edit it.")
        sys.exit(1)
    feeds = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
    run_migrations()

    failures = 0
    with SessionLocal() as db:
        for feed in feeds:
            try:
                result = import_feed(db, feed["url"], feed["category"], feed["country"], feed.get("limit", 10))
                report(f"{result.feed_title}: {len(result.created)} new drafts, "
                       f"{result.already_imported} already imported, {len(result.skipped)} skipped")
            except FeedError as exc:
                failures += 1
                report(f"FAILED {feed['url']}: {exc}")
            except Exception as exc:  # one broken feed must not stop the others
                db.rollback()
                failures += 1
                report(f"FAILED {feed['url']}: unexpected {type(exc).__name__}: {exc}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
