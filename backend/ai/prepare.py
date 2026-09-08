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


def create_article_prompt(
    title: str,
    summary: str,
    content: str,
) -> str:
    article_text = prepare_article_for_ai(
        title=title,
        summary=summary,
        content=content,
    )

    return f"""
You are a news analysis assistant.

Analyze the following news article.

Write a concise summary in English.

Identify exactly 3 key points in English.

Classify the article into exactly one of these categories:
- AI
- Programming
- Technology
- Business
- Science
- Security

ARTICLE:

{article_text}
""".strip()
