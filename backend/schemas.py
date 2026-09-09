from pydantic import BaseModel


class ArticleListResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: str
    summary: str
    ai_summary: str | None
    key_points: str | None
    category: str | None


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: str
    content: str
    summary: str
    ai_summary: str | None
    key_points: str | None
    category: str | None