import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from ai.client import analyze_article
from ai.prepare import create_article_prompt
from database import (
    create_tables,
    get_articles_without_analysis,
    get_articles_without_content,
    save_article,
    update_article_analysis,
    update_article_content,
)
from scraper.rss import fetch_article_content, fetch_news, is_news_article


FEED_URLS = [
    "https://tecnoblog.net/feed/",
]


def ingest_articles(feed_urls: list[str]) -> dict:
    new_articles = 0
    existing_articles = 0
    skipped_articles = 0
    failed_feeds = 0

    for feed_url in feed_urls:
        print(f"Fetching feed: {feed_url}")

        try:
            articles = fetch_news(feed_url)

        except Exception as error:
            failed_feeds += 1
            print(f"Feed failed: {error}")
            continue

        print(f"Found {len(articles)} articles.")

        for article in articles:
            if not is_news_article(article["url"]):
                skipped_articles += 1
                continue

            was_saved = save_article(
                {**article, "content": ""}
            )

            if was_saved:
                new_articles += 1
                print(f"Saved: {article['title']}")
            else:
                existing_articles += 1

    return {
        "new": new_articles,
        "existing": existing_articles,
        "skipped": skipped_articles,
        "failed_feeds": failed_feeds,
    }


def extract_contents() -> dict:
    articles = get_articles_without_content()

    print(f"Articles without content: {len(articles)}")

    extracted = 0
    failed = 0

    for article in articles:
        print(f"Fetching content: {article.title}")

        try:
            content = fetch_article_content(article.url)

        except Exception as error:
            failed += 1
            print(f"Content extraction failed: {error}")
            continue

        if not content:
            failed += 1
            print("Content not found.")
            continue

        update_article_content(
            article_id=article.id,
            content=content,
        )

        extracted += 1

    return {
        "extracted": extracted,
        "failed": failed,
    }


def analyze_articles() -> dict:
    articles = get_articles_without_analysis()

    print(f"Articles without AI analysis: {len(articles)}")

    analyzed = 0
    failed = 0

    for article in articles:
        print(f"Analyzing: {article.title}")

        try:
            prompt = create_article_prompt(
                title=article.title,
                summary=article.summary,
                content=article.content,
            )

            analysis = analyze_article(prompt)

            key_points_json = json.dumps(
                analysis.key_points,
                ensure_ascii=False,
            )

            update_article_analysis(
                article_id=article.id,
                ai_summary=analysis.summary,
                key_points=key_points_json,
                category=analysis.category,
            )

            analyzed += 1

        except Exception as error:
            failed += 1
            print(f"Analysis failed: {error}")

    return {
        "analyzed": analyzed,
        "failed": failed,
    }


def main():
    create_tables()

    print("=== Phase A: ingestion ===")
    ingestion = ingest_articles(FEED_URLS)

    print("")
    print("=== Phase B: content extraction ===")
    extraction = extract_contents()

    print("")
    print("=== Phase C: AI analysis ===")
    analysis = analyze_articles()

    print("")
    print("==========================================")
    print(f"New articles: {ingestion['new']}")
    print(f"Existing articles: {ingestion['existing']}")
    print(f"Skipped (not news): {ingestion['skipped']}")
    print(f"Failed feeds: {ingestion['failed_feeds']}")
    print(f"Contents extracted: {extraction['extracted']}")
    print(f"Content failures: {extraction['failed']}")
    print(f"Articles analyzed: {analysis['analyzed']}")
    print(f"Analysis failures: {analysis['failed']}")
    print("==========================================")


if __name__ == "__main__":
    main()
