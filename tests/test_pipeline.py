import json
from datetime import datetime, timezone

import database
from ai.client import ArticleAnalysis
from pipeline import run


FEED_URL = "https://example.com/feed/"
NEWS_URL = "https://example.com/noticias/a"


def _make_feed_article(url, title="Feed Article"):
    return {
        "title": title,
        "url": url,
        "published_at": datetime.now(timezone.utc),
        "summary": "A feed summary.",
    }


def _make_analysis():
    return ArticleAnalysis(
        summary="AI generated summary.",
        key_points=["ponto um", "ponto dois", "ponto três"],
        category="Technology",
    )


def _save_article(url, title="Saved Article", content=""):
    database.save_article(
        {
            "title": title,
            "url": url,
            "summary": "A test summary.",
            "content": content,
            "published_at": datetime.now(timezone.utc),
        }
    )

    return database.get_article_by_url(url)


def test_ingest_articles_saves_new_articles_with_empty_content(
    isolated_db,
    monkeypatch,
):
    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [_make_feed_article(NEWS_URL)],
    )

    result = run.ingest_articles([FEED_URL])

    saved = database.get_article_by_url(NEWS_URL)

    assert result == {"new": 1, "existing": 0, "skipped": 0, "failed_feeds": 0}
    assert saved.title == "Feed Article"
    assert saved.content == ""
    assert saved.ai_summary is None


def test_ingest_articles_skips_articles_already_in_database(
    isolated_db,
    monkeypatch,
):
    _save_article(NEWS_URL, content="Existing content.")

    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [
            _make_feed_article(NEWS_URL),
            _make_feed_article("https://example.com/noticias/b"),
        ],
    )

    result = run.ingest_articles([FEED_URL])

    existing = database.get_article_by_url(NEWS_URL)

    assert result == {"new": 1, "existing": 1, "skipped": 0, "failed_feeds": 0}
    assert existing.content == "Existing content."
    assert database.count_articles() == 2


def test_ingest_articles_skips_non_news_articles(
    isolated_db,
    monkeypatch,
):
    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [
            _make_feed_article(NEWS_URL),
            _make_feed_article("https://example.com/achados/oferta"),
            _make_feed_article("https://example.com/guias/melhor-fone"),
            _make_feed_article("https://example.com/responde/como-fazer"),
        ],
    )

    result = run.ingest_articles([FEED_URL])

    assert result == {"new": 1, "existing": 0, "skipped": 3, "failed_feeds": 0}
    assert database.count_articles() == 1
    assert database.get_article_by_url(NEWS_URL) is not None
    assert (
        database.get_article_by_url("https://example.com/achados/oferta")
        is None
    )


def test_ingest_articles_does_not_save_when_feed_has_only_non_news(
    isolated_db,
    monkeypatch,
):
    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [
            _make_feed_article("https://example.com/achados/oferta"),
        ],
    )

    result = run.ingest_articles([FEED_URL])

    assert result == {"new": 0, "existing": 0, "skipped": 1, "failed_feeds": 0}
    assert database.count_articles() == 0
    assert database.get_articles_without_content() == []


def test_ingest_articles_is_idempotent_across_runs(isolated_db, monkeypatch):
    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [_make_feed_article(NEWS_URL)],
    )

    run.ingest_articles([FEED_URL])
    result = run.ingest_articles([FEED_URL])

    assert result["new"] == 0
    assert result["existing"] == 1
    assert database.count_articles() == 1


def test_ingest_articles_continues_after_feed_failure(
    isolated_db,
    monkeypatch,
    capsys,
):
    def fake_fetch_news(feed_url):
        if feed_url == "https://broken.example.com/feed/":
            raise RuntimeError("feed unavailable")

        return [_make_feed_article(NEWS_URL)]

    monkeypatch.setattr(run, "fetch_news", fake_fetch_news)

    result = run.ingest_articles(
        ["https://broken.example.com/feed/", FEED_URL]
    )

    assert result == {"new": 1, "existing": 0, "skipped": 0, "failed_feeds": 1}
    assert "Feed failed: feed unavailable" in capsys.readouterr().out


def test_extract_contents_updates_articles_without_content(
    isolated_db,
    monkeypatch,
):
    article = _save_article("https://example.com/a")

    monkeypatch.setattr(
        run,
        "fetch_article_content",
        lambda url: "Full article content.",
    )

    result = run.extract_contents()

    updated = database.get_article_by_id(article.id)

    assert result == {"extracted": 1, "failed": 0}
    assert updated.content == "Full article content."


def test_extract_contents_ignores_articles_that_already_have_content(
    isolated_db,
    monkeypatch,
):
    article = _save_article("https://example.com/a", content="Existing.")

    def fail_if_called(url):
        raise AssertionError("fetch_article_content should not be called")

    monkeypatch.setattr(run, "fetch_article_content", fail_if_called)

    result = run.extract_contents()

    assert result == {"extracted": 0, "failed": 0}
    assert database.get_article_by_id(article.id).content == "Existing."


def test_extract_contents_counts_empty_content_as_failure(
    isolated_db,
    monkeypatch,
):
    article = _save_article("https://example.com/a")

    monkeypatch.setattr(run, "fetch_article_content", lambda url: "")

    result = run.extract_contents()

    assert result == {"extracted": 0, "failed": 1}
    assert database.get_article_by_id(article.id).content == ""


def test_extract_contents_continues_after_individual_failure(
    isolated_db,
    monkeypatch,
    capsys,
):
    failing = _save_article("https://example.com/fail", title="Failing")
    working = _save_article("https://example.com/ok", title="Working")

    def fake_fetch(url):
        if url.endswith("/fail"):
            raise RuntimeError("timeout")

        return "Working content."

    monkeypatch.setattr(run, "fetch_article_content", fake_fetch)

    result = run.extract_contents()

    assert result == {"extracted": 1, "failed": 1}
    assert database.get_article_by_id(failing.id).content == ""
    assert database.get_article_by_id(working.id).content == "Working content."
    assert "Content extraction failed: timeout" in capsys.readouterr().out


def test_analyze_articles_saves_analysis(isolated_db, monkeypatch):
    article = _save_article("https://example.com/a", content="Some content.")

    monkeypatch.setattr(
        run,
        "analyze_article",
        lambda prompt: _make_analysis(),
    )

    result = run.analyze_articles()

    updated = database.get_article_by_id(article.id)

    assert result == {"analyzed": 1, "failed": 0}
    assert updated.ai_summary == "AI generated summary."
    assert updated.category == "Technology"
    assert json.loads(updated.key_points) == [
        "ponto um",
        "ponto dois",
        "ponto três",
    ]


def test_analyze_articles_continues_after_individual_failure(
    isolated_db,
    monkeypatch,
    capsys,
):
    failing = _save_article("https://example.com/fail", title="Failing")
    working = _save_article("https://example.com/ok", title="Working")

    def fake_analyze(prompt):
        if "Failing" in prompt:
            raise RuntimeError("OpenAI unavailable")

        return _make_analysis()

    monkeypatch.setattr(run, "analyze_article", fake_analyze)

    result = run.analyze_articles()

    assert result == {"analyzed": 1, "failed": 1}
    assert database.get_article_by_id(failing.id).ai_summary is None
    assert (
        database.get_article_by_id(working.id).ai_summary
        == "AI generated summary."
    )
    assert "Analysis failed: OpenAI unavailable" in capsys.readouterr().out


def test_main_runs_full_pipeline(isolated_db, monkeypatch):
    monkeypatch.setattr(run, "create_tables", lambda: None)
    monkeypatch.setattr(run, "FEED_URLS", [FEED_URL])
    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [_make_feed_article(NEWS_URL)],
    )
    monkeypatch.setattr(
        run,
        "fetch_article_content",
        lambda url: "Full article content.",
    )
    monkeypatch.setattr(
        run,
        "analyze_article",
        lambda prompt: _make_analysis(),
    )

    run.main()

    article = database.get_article_by_url(NEWS_URL)

    assert article.content == "Full article content."
    assert article.ai_summary == "AI generated summary."
    assert article.category == "Technology"
    assert database.get_articles_without_content() == []
    assert database.get_articles_without_analysis() == []


def test_main_retries_pending_articles_on_next_run(isolated_db, monkeypatch):
    monkeypatch.setattr(run, "create_tables", lambda: None)
    monkeypatch.setattr(run, "FEED_URLS", [FEED_URL])
    monkeypatch.setattr(
        run,
        "fetch_news",
        lambda feed_url: [_make_feed_article(NEWS_URL)],
    )

    def failing_fetch(url):
        raise RuntimeError("site down")

    monkeypatch.setattr(run, "fetch_article_content", failing_fetch)
    monkeypatch.setattr(
        run,
        "analyze_article",
        lambda prompt: _make_analysis(),
    )

    run.main()

    assert len(database.get_articles_without_content()) == 1

    monkeypatch.setattr(
        run,
        "fetch_article_content",
        lambda url: "Recovered content.",
    )

    run.main()

    article = database.get_article_by_url(NEWS_URL)

    assert article.content == "Recovered content."
    assert database.get_articles_without_content() == []
