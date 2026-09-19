from pathlib import Path

from sqlalchemy import create_engine, distinct, func, select
from sqlalchemy.orm import Session

from models import Article, Base


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "news.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_tables():
    Base.metadata.create_all(engine)


def _find_article_by_url(session: Session, url: str) -> Article | None:
    statement = select(Article).where(
        Article.url == url
    )

    return session.execute(statement).scalar_one_or_none()


def _apply_article_filters(
    statement,
    category: str | None,
    search: str | None,
):
    if category:
        statement = statement.where(
            Article.category == category
        )

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            Article.title.ilike(search_pattern)
            | Article.summary.ilike(search_pattern)
        )

    return statement


def article_exists(url: str) -> bool:
    with Session(engine) as session:
        return _find_article_by_url(session, url) is not None


def save_article(article_data: dict) -> bool:
    with Session(engine) as session:
        if _find_article_by_url(session, article_data["url"]):
            return False

        article = Article(**article_data)

        session.add(article)
        session.commit()

        return True


def get_articles(
    category: str | None = None,
    search: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
):
    with Session(engine) as session:
        statement = select(Article).order_by(
            Article.published_at.desc()
        )

        statement = _apply_article_filters(statement, category, search)

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        result = session.execute(statement)

        return result.scalars().all()


def get_articles_without_analysis():
    with Session(engine) as session:
        statement = select(Article).where(
            Article.ai_summary.is_(None)
        )

        result = session.execute(statement)

        return result.scalars().all()


def get_article_by_url(url: str):
    with Session(engine) as session:
        return _find_article_by_url(session, url)


def get_article_by_id(article_id: int):
    with Session(engine) as session:
        statement = select(Article).where(
            Article.id == article_id
        )

        return session.execute(statement).scalar_one_or_none()


def get_categories():
    with Session(engine) as session:
        statement = (
            select(distinct(Article.category))
            .where(Article.category.is_not(None))
            .order_by(Article.category)
        )

        result = session.execute(statement)

        return result.scalars().all()


def count_articles(
    category: str | None = None,
    search: str | None = None,
):
    with Session(engine) as session:
        statement = select(
            func.count(Article.id)
        )

        statement = _apply_article_filters(statement, category, search)

        return session.execute(statement).scalar_one()


def update_article_content(article_id: int, content: str):
    with Session(engine) as session:
        article = session.get(Article, article_id)

        if not article:
            return False

        article.content = content

        session.commit()

        return True


def update_article_analysis(
    article_id: int,
    ai_summary: str,
    key_points: str,
    category: str,
):
    with Session(engine) as session:
        article = session.get(Article, article_id)

        if not article:
            return False

        article.ai_summary = ai_summary
        article.key_points = key_points
        article.category = category

        session.commit()

        return True


if __name__ == "__main__":
    create_tables()
    print("Database tables created.")
    