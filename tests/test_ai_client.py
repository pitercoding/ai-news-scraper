from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from ai import client as ai_client
from ai.client import ArticleAnalysis, analyze_article


ALLOWED_CATEGORIES = [
    "AI",
    "Programming",
    "Technology",
    "Business",
    "Science",
    "Security",
]


def _make_analysis_data(**overrides):
    data = {
        "summary": "A short summary.",
        "key_points": ["one", "two", "three"],
        "category": "AI",
    }

    data.update(overrides)

    return data


@pytest.mark.parametrize("category", ALLOWED_CATEGORIES)
def test_article_analysis_accepts_allowed_categories(category):
    analysis = ArticleAnalysis(**_make_analysis_data(category=category))

    assert analysis.category == category


@pytest.mark.parametrize(
    "category",
    ["Sports", "ai", "", "Tecnologia"],
)
def test_article_analysis_rejects_unknown_categories(category):
    with pytest.raises(ValidationError):
        ArticleAnalysis(**_make_analysis_data(category=category))


@pytest.mark.parametrize(
    "key_points",
    [
        [],
        ["one"],
        ["one", "two"],
        ["one", "two", "three", "four"],
    ],
)
def test_article_analysis_requires_exactly_three_key_points(key_points):
    with pytest.raises(ValidationError):
        ArticleAnalysis(**_make_analysis_data(key_points=key_points))


def test_article_analysis_requires_summary():
    data = _make_analysis_data()
    del data["summary"]

    with pytest.raises(ValidationError):
        ArticleAnalysis(**data)


def test_analyze_article_calls_openai_with_structured_output(monkeypatch):
    expected = ArticleAnalysis(**_make_analysis_data())
    calls = []

    def fake_parse(**kwargs):
        calls.append(kwargs)

        return SimpleNamespace(output_parsed=expected)

    monkeypatch.setattr(
        ai_client.client,
        "responses",
        SimpleNamespace(parse=fake_parse),
    )

    result = analyze_article("my prompt")

    assert result is expected
    assert calls == [
        {
            "model": "gpt-5-mini",
            "input": "my prompt",
            "text_format": ArticleAnalysis,
        }
    ]


def test_analyze_article_propagates_openai_errors(monkeypatch):
    def fake_parse(**kwargs):
        raise RuntimeError("OpenAI unavailable")

    monkeypatch.setattr(
        ai_client.client,
        "responses",
        SimpleNamespace(parse=fake_parse),
    )

    with pytest.raises(RuntimeError, match="OpenAI unavailable"):
        analyze_article("my prompt")
