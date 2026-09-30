from datetime import UTC, date, datetime, timedelta

import respx
from httpx import Response

from app.modules.library.models import LibraryEntry, Review
from app.modules.social.models import Activity
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


def _mock_book_detailed(
    external_id: str, title: str, *, subject: list[str], pages: int, author: str = "Bir Yazar"
) -> None:
    respx.get("https://openlibrary.org/search.json", params={"q": f'key:"/works/{external_id}"'}).mock(
        return_value=Response(
            200,
            json={
                "docs": [
                    {
                        "key": f"/works/{external_id}",
                        "title": title,
                        "author_name": [author],
                        "author_key": ["OL1A"],
                        "subject": subject,
                        "number_of_pages_median": pages,
                    }
                ]
            },
        )
    )
    respx.get(f"https://openlibrary.org/works/{external_id}.json").mock(
        return_value=Response(200, json={"title": title, "description": "test"})
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


@respx.mock
def test_user_stats_computes_totals_genres_monthly_and_highlights(client, db, user_factory):
    _mock_book_detailed("OL9301W", "Uzun Roman", subject=["drama"], pages=800, author="Yazar A")
    _mock_book_detailed("OL9302W", "Kısa Öykü", subject=["fantasy"], pages=100, author="Yazar B")
    user = user_factory(username="istatistikkullanici", email="istatistikkullanici@example.com")
    headers = auth_headers(user)

    client.put("/api/v1/library/book/OL9301W", json={"status": "completed", "rating": 9}, headers=headers)
    client.put("/api/v1/library/book/OL9302W", json={"status": "completed", "rating": 7}, headers=headers)

    entries = db.query(LibraryEntry).filter_by(user_id=user.id).all()
    for entry in entries:
        if entry.rating == 9:
            entry.finished_at = date(2024, 3, 15)
            entry.rated_at = datetime(2024, 3, 15, tzinfo=UTC)
        else:
            entry.finished_at = date(2024, 7, 10)
            entry.rated_at = datetime(2024, 7, 10, tzinfo=UTC)
    db.commit()

    response = client.get(f"/api/v1/users/{user.username}/stats", params={"year": 2024})
    assert response.status_code == 200
    body = response.json()

    assert body["totals"] == {
        "movies": 0,
        "tv": 0,
        "books": 2,
        "minutes": 0,
        "pages": 900,
        "reviews": 0,
        "avg_rating": 8.0,
    }
    assert body["rating_distribution"] == {"9": 1, "7": 1}
    assert {g["key"] for g in body["top_genres"]} == {"drama", "fantasy"}

    monthly_by_month = {m["month"]: m for m in body["monthly"]}
    assert monthly_by_month[3]["books"] == 1
    assert monthly_by_month[7]["books"] == 1
    assert monthly_by_month[1]["books"] == 0

    assert body["highlights"]["longest_book"]["external_id"] == "OL9301W"
    assert body["highlights"]["highest_rated"][0]["external_id"] == "OL9301W"


@respx.mock
def test_user_stats_year_filter_excludes_entries_from_other_years(client, db, user_factory):
    _mock_book_detailed("OL9303W", "Diğer Yıl Kitabı", subject=["drama"], pages=200)
    user = user_factory(username="yilfiltresi", email="yilfiltresi@example.com")
    client.put(
        "/api/v1/library/book/OL9303W", json={"status": "completed", "rating": 8}, headers=auth_headers(user)
    )
    entry = db.query(LibraryEntry).filter_by(user_id=user.id).first()
    entry.finished_at = date(2023, 5, 1)
    db.commit()

    response = client.get(f"/api/v1/users/{user.username}/stats", params={"year": 2024})
    assert response.status_code == 200
    body = response.json()
    assert body["totals"]["books"] == 0
    assert body["highlights"]["longest_book"] is None


def test_stats_for_unknown_user_returns_404(client):
    response = client.get("/api/v1/users/hicbiryerdeyok/stats")
    assert response.status_code == 404


@respx.mock
def test_wrapped_includes_fun_title_most_liked_review_and_active_month(client, db, user_factory):
    _mock_book_detailed("OL9304W", "Duygusal Roman", subject=["drama"], pages=300)
    user = user_factory(username="ozetkullanicisi2", email="ozetkullanicisi2@example.com")
    headers = auth_headers(user)

    client.put("/api/v1/library/book/OL9304W", json={"status": "completed", "rating": 10}, headers=headers)
    client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL9304W", "body": "Muhteşem bir kitaptı, çok etkilendim."},
        headers=headers,
    )

    entry = db.query(LibraryEntry).filter_by(user_id=user.id).first()
    entry.finished_at = date(2024, 6, 1)
    entry.rated_at = datetime(2024, 6, 1, tzinfo=UTC)
    activity = db.query(Activity).filter_by(actor_id=user.id).first()
    activity.created_at = datetime(2024, 6, 1, tzinfo=UTC)
    db.commit()

    review = db.query(Review).filter_by(user_id=user.id).first()
    review.created_at = datetime(2024, 6, 1, tzinfo=UTC)
    db.commit()

    liker = user_factory(username="begenenkullanici2", email="begenenkullanici2@example.com")
    client.post(f"/api/v1/activities/{activity.id}/like", headers=auth_headers(liker))

    response = client.get("/api/v1/users/me/wrapped", params={"year": 2024}, headers=headers)
    assert response.status_code == 200
    body = response.json()

    assert body["fun_title"] == "Duygu Avcısı"
    assert body["dominant_genre"]["key"] == "drama"
    assert body["most_active_month"] == 6
    assert body["most_liked_review"]["likes_count"] == 1
    assert body["most_liked_review"]["content"]["external_id"] == "OL9304W"
    assert body["first_completed"]["external_id"] == "OL9304W"
    assert body["last_completed"]["external_id"] == "OL9304W"
