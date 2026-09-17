from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_get_articles():
    response = client.get("/articles")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["offset"], int)

    if data["items"]:
        article = data["items"][0]

        assert "id" in article
        assert "title" in article
        assert "url" in article
        assert "published_at" in article
        assert "summary" in article
        assert "ai_summary" in article
        assert "key_points" in article
        assert "category" in article

        assert isinstance(article["id"], int)
        assert isinstance(article["title"], str)
        assert isinstance(article["url"], str)
        assert isinstance(article["published_at"], str)
        assert isinstance(article["summary"], str)

        assert article["ai_summary"] is None or isinstance(
            article["ai_summary"],
            str,
        )

        assert article["key_points"] is None or isinstance(
            article["key_points"],
            list,
        )

        assert article["category"] is None or isinstance(
            article["category"],
            str,
        )