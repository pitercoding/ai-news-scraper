from database import article_exists, get_articles, save_article
from scraper.rss import fetch_news, fetch_article_content


RSS_URL = "https://tecnoblog.net/feed/"


def main():
    articles = fetch_news(RSS_URL)

    new_articles = 0
    existing_articles = 0

    for article in articles:
        if article_exists(article["url"]):
            existing_articles += 1
            continue

        content = fetch_article_content(article["url"])

        article["content"] = content

        was_saved = save_article(article)

        if was_saved:
            new_articles += 1

    print("==========================================")
    print(f"New articles: {new_articles}")
    print(f"Existing articles: {existing_articles}")

    saved_articles = get_articles()

    print(f"Total articles in database: {len(saved_articles)}")
    print("==========================================")
    print("")

    for article in saved_articles[:3]:
        print(f"ID: {article.id}")
        print(f"Title: {article.title}")
        print(f"URL: {article.url}")
        print(f"Published: {article.published_at}")
        print(f"Summary: {article.summary}")
        print(f"Content preview: {article.content[:300]}...")
        print("-" * 80)


if __name__ == "__main__":
    main()