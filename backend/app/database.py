from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection, _record):
    # WAL lets readers and the writer work at the same time; busy_timeout
    # waits for a lock instead of failing straight away.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Parent class for every table in models.py."""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
