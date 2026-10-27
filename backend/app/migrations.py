"""Bring the database up to date. Runs automatically when the server starts."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from .config import BACKEND_DIR
from .database import engine

BASELINE = "0001"  # the tables as they were before migrations existed


def alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(Path(BACKEND_DIR / "migrations")))
    return cfg


def run_migrations() -> None:
    cfg = alembic_config()
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        tables = inspect(connection).get_table_names()
        if "posts" in tables and "alembic_version" not in tables:
            # A database created before migrations existed: mark it as baseline.
            command.stamp(cfg, BASELINE)
        command.upgrade(cfg, "head")
