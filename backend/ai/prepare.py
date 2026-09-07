def prepare_article_for_ai(
    title: str,
    summary: str,
    content: str,
    max_content_length: int = 8000,
) -> str:
    content = content[:max_content_length]

    return f"""
Title:
{title}

Summary:
{summary}

Content:
{content}
""".strip()