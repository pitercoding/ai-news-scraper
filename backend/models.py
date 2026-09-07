from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    published_at: Mapped[str] = mapped_column(String(100))
    summary: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_points: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)