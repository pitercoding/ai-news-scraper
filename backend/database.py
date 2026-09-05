from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Article, Base


DATABASE_URL = "sqlite:///./data/news.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_tables():
    Base.metadata.create_all(engine)

def article_exists(url: str) -> bool:
    with Session(engine) as session:
        statement = select(Article).where(
            Article.url == url
        )

        existing_article = session.execute(statement).scalar_one_or_none()

        return existing_article is not None

def save_article(article_data: dict) -> bool:
    with Session(engine) as session:
        statement = select(Article).where(
            Article.url == article_data["url"]
        )

        existing_article = session.execute(statement).scalar_one_or_none()

        if existing_article:
            return False

        article = Article(**article_data)

        session.add(article)
        session.commit()

        return True

def get_articles():
    with Session(engine) as session:
        statement = select(Article)
        result = session.execute(statement)

        return result.scalars().all()


if __name__ == "__main__":
    create_tables()
    print("Database tables created.")