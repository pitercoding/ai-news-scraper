from datetime import datetime
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ai-news-scraper/1.0)"
}

NEWS_SECTIONS = {"noticias"}


def is_news_article(url: str) -> bool:
    segments = [
        segment
        for segment in urlparse(url).path.split("/")
        if segment
    ]

    return len(segments) >= 2 and segments[0] in NEWS_SECTIONS


def parse_published_at(value: str) -> datetime | None:
    try:
        return datetime.strptime(
            value,
            "%a, %d %b %Y %H:%M:%S %z",
        )
    except ValueError:
        return None


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
        published_at = parse_published_at(
            entry.get("published", "")
        )

        if published_at is None:
            print(
                f"Skipping article with invalid date: {entry.get('title', '')}"
            )
            continue

        article = {
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published_at": published_at,
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