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

Classify the article into exactly one of these categories, choosing the one
that best matches the article's PRIMARY subject:
- AI: articles primarily about artificial intelligence: AI models, agents, AI companies and research, AI safety, or the impact of AI. A product or piece of hardware that merely includes AI features belongs in Technology.
- Programming: software development, programming languages, frameworks, libraries, and developer tools.
- Technology: devices, hardware, operating systems, apps, telecom and internet services, and product launches.
- Business: companies and markets: deals, acquisitions, pricing, subscriptions, competition, earnings, and economic regulation.
- Science: scientific research and discoveries, space, health, and the environment.
- Security: cybersecurity: vulnerabilities, data breaches, malware, privacy, and fraud or scam prevention. Do not use it for physical safety or for general regulation.

ARTICLE:

{article_text}
""".strip()
