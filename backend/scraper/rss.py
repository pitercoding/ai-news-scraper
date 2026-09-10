from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ai-news-scraper/1.0)"
}


def parse_published_at(value: str) -> datetime:
    return datetime.strptime(
        value,
        "%a, %d %b %Y %H:%M:%S %z",
    )


def clean_summary(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    first_paragraph = soup.find("p")

    if first_paragraph:
        return first_paragraph.get_text(strip=True)

    return ""


def clean_content(text: str) -> str:
    return " ".join(text.split())


def fetch_news(rss_url: str) -> list[dict]:
    response = requests.get(
        rss_url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    feed = feedparser.parse(response.content)

    articles = []

    for entry in feed.entries:
        article = {
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published_at": parse_published_at(
                entry.get("published", "")
            ),
            "summary": clean_summary(entry.get("summary", "")),
        }

        articles.append(article)

    return articles


def fetch_article_content(url: str) -> str:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    article_content = soup.find("div", class_="entry")

    if not article_content:
        return ""

    content_parts = []

    for element in article_content.find_all(
        ["p", "h2"],
        class_=lambda classes: classes
        and (
            "wp-block-paragraph" in classes
            or "wp-block-heading" in classes
        )
    ):
        text = element.get_text(
            " ",
            strip=True
        )

        text = clean_content(text)

        if text:
            content_parts.append(text)

    return "\n\n".join(content_parts)