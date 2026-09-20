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
        assert f"- {category}\n" in prompt


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
