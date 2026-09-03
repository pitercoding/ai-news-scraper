from scraper.rss import fetch_news


RSS_URL = "https://tecnoblog.net/feed/"


def main():
    articles = fetch_news(RSS_URL)

    for article in articles[:3]:
        print("TITLE:")
        print(article["title"])

        print("\nSUMMARY:")
        print(article["summary"])

        print("\nURL:")
        print(article["url"])

        print("\nPUBLISHED AT:")
        print(article["published_at"])

        print("=" * 80)


if __name__ == "__main__":
    main()