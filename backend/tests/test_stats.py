from datetime import UTC, datetime, timedelta

import respx
from httpx import Response

from app.modules.library.models import LibraryEntry
from tests.conftest import auth_headers


def _mock_book(external_id: str, index: int) -> None:
    respx.get("https://openlibrary.org/search.json", params={"q": f'key:"/works/{external_id}"'}).mock(
        return_value=Response(
            200, json={"docs": [{"key": f"/works/{external_id}", "title": f"Kitap {index}"}]}
        )
    )
    respx.get(f"https://openlibrary.org/works/{external_id}.json").mock(
        return_value=Response(200, json={"title": f"Kitap {index}", "description": "test"})
    )


@respx.mock
def test_profile_summary_counts_entries_reviews_lists_and_favorites(client, user_factory):
    _mock_book("OL9001W", 1)
    user = user_factory(username="ozetkullanici", email="ozetkullanici@example.com")
    headers = auth_headers(user)

    client.put(
        "/api/v1/library/book/OL9001W",
        json={"status": "completed", "rating": 9, "is_favorite": True},
        headers=headers,
    )
    client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL9001W", "body": "Gerçekten çok iyi bir kitaptı."},
        headers=headers,
    )
    client.post("/api/v1/lists", json={"title": "Test Listem"}, headers=headers)

    response = client.get(f"/api/v1/users/{user.username}/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["books_completed"] == 1
    assert body["ratings"] == 1
    assert body["reviews"] == 1
    assert body["lists"] == 1
    assert body["favorites"] == 1


@respx.mock
def test_top_rated_orders_by_score_and_requires_at_least_one_vote(client, user_factory):
    _mock_book("OL9101W", 1)
    _mock_book("OL9102W", 2)
    _mock_book("OL9103W", 3)

    raters = [user_factory(username=f"puanci{i}", email=f"puanci{i}@example.com") for i in range(3)]
    for r in raters:
        client.put("/api/v1/library/book/OL9101W", json={"rating": 8}, headers=auth_headers(r))
        client.put("/api/v1/library/book/OL9102W", json={"rating": 4}, headers=auth_headers(r))
    # OL9103W hiç puanlanmadı -> listede görünmemeli
    client.put("/api/v1/library/book/OL9103W", json={"status": "planned"}, headers=auth_headers(raters[0]))

    response = client.get("/api/v1/platform/top-rated", params={"type": "book"})
    assert response.status_code == 200
    external_ids = [item["external_id"] for item in response.json()["items"]]
    assert external_ids.index("OL9101W") < external_ids.index("OL9102W")
    assert "OL9103W" not in external_ids


@respx.mock
def test_popular_widens_to_all_time_when_recent_window_too_small(client, db, user_factory):
    _mock_book("OL9201W", 1)
    user = user_factory(username="populerkullanici", email="populerkullanici@example.com")
    client.put("/api/v1/library/book/OL9201W", json={"status": "completed"}, headers=auth_headers(user))

    entry = db.query(LibraryEntry).filter_by(user_id=user.id).first()
    entry.created_at = datetime.now(UTC) - timedelta(days=100)
    db.commit()

    response = client.get("/api/v1/platform/popular", params={"type": "book", "days": 7})
    assert response.status_code == 200
    external_ids = [item["external_id"] for item in response.json()]
    assert "OL9201W" in external_ids
