import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from database import get_articles, update_article_content
from scraper.rss import fetch_article_content


def main():
    articles = get_articles()

    print(f"Articles to reprocess: {len(articles)}")

    for article in articles:
        print(f"Reprocessing: {article.title}")

        content = fetch_article_content(article.url)

        if not content:
            print("Content not found.")
            continue

        update_article_content(
            article_id=article.id,
            content=content,
        )

        print("Content updated.")


if __name__ == "__main__":
    main()