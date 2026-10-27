"""Database tables. Any change here needs a migration: see migrations/README.md."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Original article for stories brought in by the news importer
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True, unique=True)
    # "draft" posts are only visible to the admin
    status: Mapped[str] = mapped_column(String(20), default="published", server_default="published")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Podcast(Base):
    __tablename__ = "podcasts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    host: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(50))
    external_url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
