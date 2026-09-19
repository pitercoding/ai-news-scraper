import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import database
from models import Article, Base


SEED_ARTICLES = [
    {
        "title": "Python 3.13 released with new features",
        "url": "https://example.com/python-3-13",
        "summary": "A summary about python performance improvements.",
        "content": "Full content about the python 3.13 release.",
        "category": "Programming",
        "ai_summary": "Python 3.13 brings faster performance.",
        "key_points": ["Faster startup", "Better errors", "New syntax"],
        "days_ago": 0,
    },
    {
        "title": "New AI model beats benchmarks",
        "url": "https://example.com/ai-model-benchmarks",
        "summary": "AI research summary with record results.",
        "content": "Full content about the new AI model.",
        "category": "AI",
        "ai_summary": "A new AI model sets a benchmark record.",
        "key_points": ["State of the art", "Open weights"],
        "days_ago": 1,
    },
    {
        "title": "Security vulnerability found in popular library",
        "url": "https://example.com/security-vulnerability",
        "summary": "A critical security bug was disclosed.",
        "content": "Full content about the security vulnerability.",
        "category": "Security",
        "ai_summary": None,
        "key_points": None,
        "days_ago": 2,
    },
    {
        "title": "Business quarterly report shows growth",
        "url": "https://example.com/business-quarterly-report",
        "summary": "Revenue is up this quarter.",
        "content": "Full content about the quarterly report.",
        "category": "Business",
        "ai_summary": "Revenue grew compared to last quarter.",
        "key_points": ["Revenue up", "New markets"],
        "days_ago": 3,
    },
    {
        "title": "Deep dive into python asyncio internals",
        "url": "https://example.com/python-asyncio-internals",
        "summary": "How python asyncio schedules coroutines.",
        "content": "Full content about python asyncio internals.",
        "category": "Programming",
        "ai_summary": None,
        "key_points": None,
        "days_ago": 4,
    },
    {
        "title": "AI-powered python code generator launches",
        "url": "https://example.com/ai-python-code-generator",
        "summary": "A new tool generates python code with AI assistance.",
        "content": "Full content about the AI python code generator.",
        "category": "AI",
        "ai_summary": "The tool writes python code from natural language.",
        "key_points": ["Natural language input", "Python output"],
        "days_ago": 5,
    },
]


def _seed_articles(engine):
    now = datetime.now(timezone.utc)

    with Session(engine) as session:
        for article_data in SEED_ARTICLES:
            key_points = article_data["key_points"]

            session.add(
                Article(
                    title=article_data["title"],
                    url=article_data["url"],
                    summary=article_data["summary"],
                    content=article_data["content"],
                    category=article_data["category"],
                    ai_summary=article_data["ai_summary"],
                    key_points=(
                        json.dumps(key_points) if key_points else None
                    ),
                    published_at=now - timedelta(days=article_data["days_ago"]),
                )
            )

        session.commit()


@pytest.fixture(scope="session", autouse=True)
def test_database():
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_file.close()

    test_engine = create_engine(
        f"sqlite:///{db_file.name}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(test_engine)
    _seed_articles(test_engine)

    original_engine = database.engine
    database.engine = test_engine

    yield

    database.engine = original_engine

    test_engine.dispose()
    Path(db_file.name).unlink(missing_ok=True)
