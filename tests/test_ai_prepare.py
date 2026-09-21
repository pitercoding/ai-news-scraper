from typing import get_args

from ai.client import ArticleAnalysis
from ai.prepare import create_article_prompt, prepare_article_for_ai


def test_prepare_article_for_ai_includes_title_summary_and_content():
    text = prepare_article_for_ai(
        title="My title",
        summary="My summary",
        content="My content",
    )

    assert text == (
        "Title:\nMy title\n\n"
        "Summary:\nMy summary\n\n"
        "Content:\nMy content"
    )


def test_prepare_article_for_ai_truncates_content_to_default_limit():
    text = prepare_article_for_ai(
        title="Title",
        summary="Summary",
        content="#" * 9000,
    )

    assert text.count("#") == 8000


def test_prepare_article_for_ai_keeps_content_under_the_limit():
    text = prepare_article_for_ai(
        title="Title",
        summary="Summary",
        content="#" * 100,
    )

    assert text.count("#") == 100


def test_prepare_article_for_ai_respects_custom_limit():
    text = prepare_article_for_ai(
        title="Title",
        summary="Summary",
        content="#" * 100,
        max_content_length=10,
    )

    assert text.count("#") == 10


def test_prepare_article_for_ai_handles_empty_content():
    text = prepare_article_for_ai(
        title="Title",
        summary="Summary",
        content="",
    )

    assert text.endswith("Content:")


def test_create_article_prompt_requests_summary_key_points_and_category():
    prompt = create_article_prompt(
        title="Title",
        summary="Summary",
        content="Content",
    )

    assert "summary in English" in prompt
    assert "exactly 3 key points" in prompt
    assert "exactly one of these categories" in prompt


def test_create_article_prompt_lists_all_allowed_categories():
    prompt = create_article_prompt(
        title="Title",
        summary="Summary",
        content="Content",
    )

    for category in [
        "AI",
        "Programming",
        "Technology",
        "Business",
        "Science",
        "Security",
    ]:
        assert f"- {category}: " in prompt


def test_create_article_prompt_lists_exactly_the_schema_categories():
    prompt = create_article_prompt(
        title="Title",
        summary="Summary",
        content="Content",
    )

    schema_categories = set(
        get_args(ArticleAnalysis.model_fields["category"].annotation)
    )

    prompt_categories = {
        line[2:].split(":")[0]
        for line in prompt.split("ARTICLE:")[0].splitlines()
        if line.startswith("- ")
    }

    assert prompt_categories == schema_categories


def test_create_article_prompt_defines_categories_by_primary_subject():
    prompt = create_article_prompt(
        title="Title",
        summary="Summary",
        content="Content",
    )

    assert "PRIMARY subject" in prompt
    assert "merely includes AI features belongs in Technology" in prompt
    assert "cybersecurity" in prompt
    assert "Do not use it for physical safety" in prompt


def test_create_article_prompt_puts_article_after_instructions():
    prompt = create_article_prompt(
        title="Unique title",
        summary="Summary",
        content="Content",
    )

    assert prompt.index("ARTICLE:") > prompt.index("exactly 3 key points")
    assert prompt.index("Unique title") > prompt.index("ARTICLE:")


def test_create_article_prompt_truncates_long_content():
    prompt = create_article_prompt(
        title="Title",
        summary="Summary",
        content="#" * 9000,
    )

    assert prompt.count("#") == 8000
