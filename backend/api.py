from fastapi import FastAPI, HTTPException

from database import (
    count_articles,
    get_article_by_id,
    get_articles,
)
from schemas import (
    ArticleListResponse,
    ArticlePaginationResponse,
    ArticleResponse,
)

app = FastAPI(
    title="AI News Scraper API",
    description="REST API for AI-powered news analysis",
    version="1.0.0",
)


@app.get(
    "/articles",
    response_model=ArticlePaginationResponse,
)
def list_articles(
    category: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    articles = get_articles(
        category=category,
        search=search,
        limit=limit,
        offset=offset,
    )

    total = count_articles(
        category=category,
        search=search,
    )

    return {
        "items": articles,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@app.get(
    "/articles/{article_id}",
    response_model=ArticleResponse,
)
def get_article(article_id: int):
    article = get_article_by_id(article_id)

    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    return article
