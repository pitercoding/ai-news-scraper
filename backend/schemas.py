import json
from datetime import datetime

from pydantic import BaseModel, field_validator


class ArticleListResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: datetime
    summary: str
    ai_summary: str | None
    key_points: list[str] | None
    category: str | None

    @field_validator("key_points", mode="before")
    @classmethod
    def parse_key_points(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            return json.loads(value)

        return value


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: datetime
    content: str
    summary: str
    ai_summary: str | None
    key_points: list[str] | None
    category: str | None

    @field_validator("key_points", mode="before")
    @classmethod
    def parse_key_points(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            return json.loads(value)

        return value


class ArticlePaginationResponse(BaseModel):
    items: list[ArticleListResponse]
    total: int
    limit: int
    offset: int