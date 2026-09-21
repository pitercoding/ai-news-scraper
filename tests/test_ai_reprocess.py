import json
from datetime import datetime, timezone

import database
from ai import reprocess
from ai.client import ArticleAnalysis


def _save_article(url, title="Test Article"):
    database.save_article(
        {
            "title": title,
            "url": url,
            "summary": "A test summary.",
            "content": "Test content.",
            "published_at": datetime.now(timezone.utc),
        }
    )

    return database.get_article_by_url(url)


def _make_analysis(**overrides):
    data = {
        "summary": "AI generated summary.",
        "key_points": ["ponto um", "ponto dois", "ponto três"],
        "category": "Technology",
    }

    data.update(overrides)

    return ArticleAnalysis(**data)


def test_main_saves_analysis_for_articles_without_analysis(
    isolated_db,
    monkeypatch,
):
    article = _save_article("https://example.com/a")

    monkeypatch.setattr(
        reprocess,
        "analyze_article",
        lambda prompt: _make_analysis(),
    )

    reprocess.main()

    updated = database.get_article_by_id(article.id)

    assert updated.ai_summary == "AI generated summary."
    assert updated.category == "Technology"
    assert json.loads(updated.key_points) == [
        "ponto um",
        "ponto dois",
        "ponto três",
    ]
    assert database.get_articles_without_analysis() == []


def test_main_keeps_non_ascii_key_points_readable(isolated_db, monkeypatch):
    article = _save_article("https://example.com/a")

    monkeypatch.setattr(
        reprocess,
        "analyze_article",
        lambda prompt: _make_analysis(),
    )

    reprocess.main()

    updated = database.get_article_by_id(article.id)

    assert "três" in updated.key_points


def test_main_sends_article_prompt_to_ai(isolated_db, monkeypatch):
    _save_article("https://example.com/a", title="Unique title")

    prompts = []

    def fake_analyze(prompt):
        prompts.append(prompt)

        return _make_analysis()

    monkeypatch.setattr(reprocess, "analyze_article", fake_analyze)

    reprocess.main()

    assert len(prompts) == 1
    assert "Unique title" in prompts[0]
    assert "Test content." in prompts[0]


def test_main_does_nothing_when_all_articles_are_analyzed(
    isolated_db,
    monkeypatch,
):
    article = _save_article("https://example.com/a")

    database.update_article_analysis(
        article_id=article.id,
        ai_summary="Existing summary.",
        key_points=json.dumps(["a", "b", "c"]),
        category="AI",
    )

    def fail_if_called(prompt):
        raise AssertionError("analyze_article should not be called")

    monkeypatch.setattr(reprocess, "analyze_article", fail_if_called)

    reprocess.main()

    unchanged = database.get_article_by_id(article.id)

    assert unchanged.ai_summary == "Existing summary."


def test_main_skips_articles_without_content(isolated_db, monkeypatch):
    database.save_article(
        {
            "title": "No content yet",
            "url": "https://example.com/no-content",
            "summary": "A test summary.",
            "content": "",
            "published_at": datetime.now(timezone.utc),
        }
    )

    prompts = []

    def fake_analyze(prompt):
        prompts.append(prompt)

        return _make_analysis()

    monkeypatch.setattr(reprocess, "analyze_article", fake_analyze)

    reprocess.main()

    article = database.get_article_by_url("https://example.com/no-content")

    assert prompts == []
    assert article.ai_summary is None


def test_main_continues_after_individual_failure(
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

    monkeypatch.setattr(reprocess, "analyze_article", fake_analyze)

    reprocess.main()

    failed_article = database.get_article_by_id(failing.id)
    saved_article = database.get_article_by_id(working.id)

    assert failed_article.ai_summary is None
    assert saved_article.ai_summary == "AI generated summary."

    assert "Analysis failed: OpenAI unavailable" in capsys.readouterr().out


def test_main_leaves_failed_article_available_for_retry(
    isolated_db,
    monkeypatch,
):
    article = _save_article("https://example.com/a")

    def always_fail(prompt):
        raise RuntimeError("boom")

    monkeypatch.setattr(reprocess, "analyze_article", always_fail)

    reprocess.main()

    pending = database.get_articles_without_analysis()

    assert [item.id for item in pending] == [article.id]
