from fastapi.testclient import TestClient

from api import app
from database import get_articles_without_analysis

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


def test_get_articles_with_category_and_search():
    response = client.get(
        "/articles?category=AI&search=python",
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data

    for article in data["items"]:
        assert article["category"] == "AI"

        title = article["title"].lower()
        summary = article["summary"].lower()

        assert "python" in title or "python" in summary


def test_get_article_by_id():
    articles_response = client.get("/articles")

    assert articles_response.status_code == 200

    articles_data = articles_response.json()

    assert articles_data["items"]

    article_id = articles_data["items"][0]["id"]

    response = client.get(
        f"/articles/{article_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == article_id
    assert "title" in data
    assert "url" in data
    assert "published_at" in data
    assert "summary" in data
    assert "content" in data
    assert "ai_summary" in data
    assert "key_points" in data
    assert "category" in data

    assert isinstance(data["id"], int)
    assert isinstance(data["title"], str)
    assert isinstance(data["url"], str)
    assert isinstance(data["published_at"], str)
    assert isinstance(data["summary"], str)
    assert isinstance(data["content"], str)


def test_get_article_not_found():
    response = client.get(
        "/articles/999999",
    )

    assert response.status_code == 404


def test_get_categories():
    response = client.get("/categories")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    for category in data:
        assert isinstance(category, str)


def test_get_articles_with_invalid_limit():
    response = client.get(
        "/articles?limit=0",
    )

    assert response.status_code == 422


def test_get_articles_with_limit_too_large():
    response = client.get(
        "/articles?limit=101",
    )

    assert response.status_code == 422


def test_get_articles_with_negative_offset():
    response = client.get(
        "/articles?offset=-1",
    )

    assert response.status_code == 422


def test_get_articles_with_invalid_limit_type():
    response = client.get(
        "/articles?limit=abc",
    )

    assert response.status_code == 422


def test_get_articles_with_invalid_offset_type():
    response = client.get(
        "/articles?offset=abc",
    )

    assert response.status_code == 422


def test_get_articles_with_search_no_results():
    response = client.get(
        "/articles?search=xyznonexistentterm",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_get_articles_with_category_no_results():
    response = client.get(
        "/articles?category=NonexistentCategory",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_get_articles_with_default_pagination():
    response = client.get("/articles")

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 20
    assert data["offset"] == 0


def test_get_articles_with_max_limit():
    response = client.get(
        "/articles?limit=100",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 100


PENDING_TITLES = {
    "Security vulnerability found in popular library",
    "Deep dive into python asyncio internals",
}


def test_get_articles_excludes_articles_without_analysis():
    response = client.get("/articles?limit=100")

    assert response.status_code == 200

    data = response.json()

    titles = {article["title"] for article in data["items"]}

    assert data["total"] == 4
    assert len(data["items"]) == 4
    assert titles.isdisjoint(PENDING_TITLES)

    for article in data["items"]:
        assert article["ai_summary"] is not None


def test_get_articles_total_matches_visible_articles_across_pages():
    first = client.get("/articles?limit=2&offset=0").json()
    second = client.get("/articles?limit=2&offset=2").json()
    beyond = client.get("/articles?limit=2&offset=4").json()

    assert first["total"] == second["total"] == beyond["total"] == 4
    assert len(first["items"]) == 2
    assert len(second["items"]) == 2
    assert beyond["items"] == []

    ids = [a["id"] for a in first["items"] + second["items"]]

    assert len(set(ids)) == 4


def test_get_articles_search_does_not_return_pending_articles():
    python_response = client.get("/articles?search=python").json()
    pending_only_response = client.get("/articles?search=asyncio").json()

    assert python_response["total"] == 2
    assert all(
        article["title"] not in PENDING_TITLES
        for article in python_response["items"]
    )

    assert pending_only_response["items"] == []
    assert pending_only_response["total"] == 0


def test_get_articles_category_filter_does_not_return_pending_articles():
    response = client.get("/articles?category=Security").json()

    assert response["items"] == []
    assert response["total"] == 0


def test_get_article_by_id_still_returns_pending_article():
    pending = get_articles_without_analysis()[0]

    response = client.get(f"/articles/{pending.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == pending.id
    assert data["ai_summary"] is None