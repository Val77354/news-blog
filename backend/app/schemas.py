from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    content: str
    author: str
    category: str
    country: str
    image_url: str | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class PostOut(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PodcastBase(BaseModel):
    title: str
    host: str
    description: str
    cover_image_url: str | None = None
    source: str
    external_url: str


class PodcastCreate(PodcastBase):
    pass


class PodcastUpdate(PodcastBase):
    pass


class PodcastOut(PodcastBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
