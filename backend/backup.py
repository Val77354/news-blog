"""Back up the database and uploaded images.

    python backup.py

Makes a safe copy of the database (even while the server is running) named
news_blog-YYYY-MM-DD_HHMM.db in BACKUP_DIR, keeps the newest KEEP_BACKUPS
copies, and mirrors the uploads folder. Scheduled nightly on this PC via
Windows Task Scheduler ("DailyCurrentBackup").
"""

import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.config import BACKEND_DIR, settings  # noqa: E402

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", str(BACKEND_DIR / "backups")))
KEEP_BACKUPS = int(os.getenv("KEEP_BACKUPS", "14"))


def database_path() -> Path:
    prefix = "sqlite:///"
    if not settings.database_url.startswith(prefix):
        sys.exit("backup.py only supports SQLite databases.")
    return Path(settings.database_url.removeprefix(prefix))


def main() -> None:
    source = database_path()
    if not source.exists():
        sys.exit(f"Database not found: {source}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    target = BACKUP_DIR / f"news_blog-{datetime.now():%Y-%m-%d_%H%M}.db"
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)  # consistent snapshot, safe while the server is running
    with sqlite3.connect(target) as check:
        if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            sys.exit(f"Backup failed its integrity check: {target}")

    old = sorted(BACKUP_DIR.glob("news_blog-*.db"))[:-KEEP_BACKUPS]
    for path in old:
        path.unlink()

    if settings.upload_dir.exists():
        shutil.copytree(settings.upload_dir, BACKUP_DIR / "uploads", dirs_exist_ok=True)

    print(f"Backed up to {target}")


if __name__ == "__main__":
    main()
