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


def test_get_articles_with_pagination():
    response = client.get(
        "/articles?limit=2&offset=0",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) <= 2


def test_get_articles_with_offset():
    first_response = client.get(
        "/articles?limit=2&offset=0",
    )

    second_response = client.get(
        "/articles?limit=2&offset=2",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert len(first_data["items"]) <= 2
    assert len(second_data["items"]) <= 2

    if first_data["items"] and second_data["items"]:
        first_ids = [article["id"] for article in first_data["items"]]

        second_ids = [article["id"] for article in second_data["items"]]

        assert first_ids != second_ids


def test_get_articles_with_category():
    response = client.get(
        "/articles?category=AI",
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data

    for article in data["items"]:
        assert article["category"] == "AI"


def test_get_articles_with_search():
    response = client.get(
        "/articles?search=python",
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data

    for article in data["items"]:
        title = article["title"].lower()
        summary = article["summary"].lower()

        assert "python" in title or "python" in summary