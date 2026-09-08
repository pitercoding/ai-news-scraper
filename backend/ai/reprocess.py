import json

from ai.client import analyze_article
from ai.prepare import create_article_prompt
from database import (
    get_articles_without_analysis,
    update_article_analysis,
)


def main():
    articles = get_articles_without_analysis()

    print(f"Articles without AI analysis: {len(articles)}")

    for article in articles:
        print(f"Analyzing: {article.title}")

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

        print("Analysis saved.")
        print("-" * 80)


if __name__ == "__main__":
    main()