import feedparser
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ai-news-scraper/1.0)"
}


def clean_summary(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    first_paragraph = soup.find("p")

    if first_paragraph:
        return first_paragraph.get_text(strip=True)

    return ""


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
            "published_at": entry.get("published", ""),
            "summary": clean_summary(entry.get("summary", "")),
        }

        articles.append(article)

    return articles