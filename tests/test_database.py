import json
from datetime import datetime, timezone

import database


def _make_article_data(**overrides):
    data = {
        "title": "Test Article",
        "url": "https://example.com/test-article",
        "summary": "A test summary.",
        "content": "Test content.",
        "published_at": datetime.now(timezone.utc),
    }

    data.update(overrides)

    return data


def test_article_exists_returns_true_for_known_url():
    assert database.article_exists("https://example.com/python-3-13") is True


def test_article_exists_returns_false_for_unknown_url():
    assert database.article_exists("https://example.com/does-not-exist") is False


def test_get_article_by_url_returns_matching_article():
    article = database.get_article_by_url(
        "https://example.com/python-3-13"
    )

    assert article is not None
    assert article.title == "Python 3.13 released with new features"


def test_get_article_by_url_returns_none_for_unknown_url():
    article = database.get_article_by_url(
        "https://example.com/does-not-exist"
    )

    assert article is None


def test_get_article_by_id_returns_none_for_unknown_id():
    assert database.get_article_by_id(999999) is None


def test_get_categories_returns_sorted_distinct_categories():
    categories = database.get_categories()

    assert categories == ["AI", "Business", "Programming", "Security"]


def test_get_articles_orders_by_published_at_desc():
    articles = database.get_articles()

    titles = [article.title for article in articles]

    assert titles == [
        "Python 3.13 released with new features",
        "New AI model beats benchmarks",
        "Security vulnerability found in popular library",
        "Business quarterly report shows growth",
        "Deep dive into python asyncio internals",
        "AI-powered python code generator launches",
    ]


def test_count_articles_by_category():
    assert database.count_articles(category="AI") == 2


def test_count_articles_by_search():
    assert database.count_articles(search="python") == 3


def test_count_articles_by_category_and_search():
    assert database.count_articles(category="AI", search="python") == 1


def test_get_articles_without_analysis_returns_only_unanalyzed_articles():
    articles = database.get_articles_without_analysis()

    titles = {article.title for article in articles}

    assert titles == {
        "Security vulnerability found in popular library",
        "Deep dive into python asyncio internals",
    }

    assert all(article.ai_summary is None for article in articles)


def test_save_article_creates_new_article(isolated_db):
    was_saved = database.save_article(_make_article_data())

    assert was_saved is True

    saved_article = database.get_article_by_url(
        "https://example.com/test-article"
    )

    assert saved_article is not None
    assert saved_article.title == "Test Article"


def test_save_article_returns_false_for_duplicate_url(isolated_db):
    article_data = _make_article_data()

    database.save_article(article_data)
    was_saved_again = database.save_article(article_data)

    assert was_saved_again is False


def test_update_article_content_updates_existing_article(isolated_db):
    database.save_article(_make_article_data())

    article = database.get_article_by_url(
        "https://example.com/test-article"
    )

    was_updated = database.update_article_content(
        article_id=article.id,
        content="Updated content.",
    )

    assert was_updated is True

    updated_article = database.get_article_by_id(article.id)

    assert updated_article.content == "Updated content."


def test_update_article_content_returns_false_for_unknown_id(isolated_db):
    was_updated = database.update_article_content(
        article_id=999999,
        content="Updated content.",
    )

    assert was_updated is False


def test_update_article_analysis_updates_existing_article(isolated_db):
    database.save_article(_make_article_data())

    article = database.get_article_by_url(
        "https://example.com/test-article"
    )

    was_updated = database.update_article_analysis(
        article_id=article.id,
        ai_summary="AI generated summary.",
        key_points=json.dumps(["point 1", "point 2"]),
        category="AI",
    )

    assert was_updated is True

    updated_article = database.get_article_by_id(article.id)

    assert updated_article.ai_summary == "AI generated summary."
    assert updated_article.key_points == json.dumps(["point 1", "point 2"])
    assert updated_article.category == "AI"


def test_update_article_analysis_returns_false_for_unknown_id():
    was_updated = database.update_article_analysis(
        article_id=999999,
        ai_summary="AI generated summary.",
        key_points=json.dumps(["point 1"]),
        category="AI",
    )

    assert was_updated is False
