import json
from pathlib import Path

import respx
from httpx import Response

from app.modules.library.models import LibraryEntry
from tests.conftest import auth_headers

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _mock_book_detail() -> None:
    respx.get("https://openlibrary.org/search.json", params={"q": 'key:"/works/OL45804W"'}).mock(
        return_value=Response(200, json=_load("ol_search_key_OL45804W.json"))
    )
    respx.get("https://openlibrary.org/works/OL45804W.json").mock(
        return_value=Response(200, json=_load("ol_work_OL45804W.json"))
    )


@respx.mock
def test_upsert_partial_update_and_null_clears_fields(client, user_factory):
    _mock_book_detail()
    user = user_factory(username="kutuphaneci", email="kutuphaneci@example.com")
    headers = auth_headers(user)

    first = client.put(
        "/api/v1/library/book/OL45804W", json={"status": "in_progress", "rating": 7}, headers=headers
    )
    assert first.status_code == 200
    body = first.json()
    assert body["status"] == "in_progress"
    assert body["rating"] == 7
    assert body["started_at"] is not None

    second = client.put("/api/v1/library/book/OL45804W", json={"rating": None}, headers=headers)
    assert second.status_code == 200
    body2 = second.json()
    assert body2["rating"] is None
    assert body2["status"] == "in_progress"


@respx.mock
def test_rating_out_of_range_returns_422(client, user_factory):
    _mock_book_detail()
    user = user_factory(username="puanhata", email="puanhata@example.com")
    response = client.put("/api/v1/library/book/OL45804W", json={"rating": 11}, headers=auth_headers(user))
    assert response.status_code == 422


@respx.mock
def test_entry_deleted_when_becomes_empty(client, db, user_factory):
    _mock_book_detail()
    user = user_factory(username="silinsin", email="silinsin@example.com")
    headers = auth_headers(user)

    client.put("/api/v1/library/book/OL45804W", json={"is_favorite": True}, headers=headers)
    assert db.query(LibraryEntry).filter_by(user_id=user.id).count() == 1

    response = client.put("/api/v1/library/book/OL45804W", json={"is_favorite": False}, headers=headers)
    assert response.status_code == 200
    assert db.query(LibraryEntry).filter_by(user_id=user.id).count() == 0


@respx.mock
def test_completed_status_sets_finished_at_automatically(client, user_factory):
    _mock_book_detail()
    user = user_factory(username="tariher", email="tariher@example.com")
    response = client.put(
        "/api/v1/library/book/OL45804W", json={"status": "completed"}, headers=auth_headers(user)
    )
    assert response.status_code == 200
    assert response.json()["finished_at"] is not None


@respx.mock
def test_content_state_reports_platform_average_and_distribution(client, user_factory):
    _mock_book_detail()
    user_a = user_factory(username="oyuncua", email="oyuncua@example.com")
    user_b = user_factory(username="oyuncub", email="oyuncub@example.com")

    client.put("/api/v1/library/book/OL45804W", json={"rating": 8}, headers=auth_headers(user_a))
    client.put("/api/v1/library/book/OL45804W", json={"rating": 10}, headers=auth_headers(user_b))

    response = client.get("/api/v1/library/book/OL45804W/state")
    assert response.status_code == 200
    body = response.json()
    assert body["platform"]["count"] == 2
    assert body["platform"]["average"] == 9.0
    assert body["platform"]["distribution"]["8"] == 1
    assert body["platform"]["distribution"]["10"] == 1


@respx.mock
def test_lookup_returns_status_for_known_and_unknown_keys(client, user_factory):
    _mock_book_detail()
    user = user_factory(username="topluarama", email="topluarama@example.com")
    headers = auth_headers(user)
    client.put("/api/v1/library/book/OL45804W", json={"status": "planned"}, headers=headers)

    response = client.post(
        "/api/v1/library/lookup",
        json={"keys": ["book:OL45804W", "book:OL999999W"]},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["book:OL45804W"]["status"] == "planned"
    assert body["book:OL999999W"]["status"] is None


@respx.mock
def test_review_duplicate_returns_409(client, user_factory):
    _mock_book_detail()
    user = user_factory(username="incelemeci", email="incelemeci@example.com")
    headers = auth_headers(user)
    payload = {
        "type": "book",
        "external_id": "OL45804W",
        "body": "Gayet iyi bir kitaptı, tavsiye ederim.",
    }

    first = client.post("/api/v1/reviews", json=payload, headers=headers)
    assert first.status_code == 201
    second = client.post("/api/v1/reviews", json=payload, headers=headers)
    assert second.status_code == 409
    assert second.json()["code"] == "REVIEW_EXISTS"


@respx.mock
def test_review_edit_by_non_owner_returns_403(client, user_factory):
    _mock_book_detail()
    owner = user_factory(username="sahip", email="sahip@example.com")
    other = user_factory(username="baskasi", email="baskasi@example.com")

    create = client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL45804W", "body": "Güzel bir kitaptı, beğendim."},
        headers=auth_headers(owner),
    )
    review_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/reviews/{review_id}", json={"body": "değiştirdim"}, headers=auth_headers(other)
    )
    assert response.status_code == 403


@respx.mock
def test_review_too_short_returns_422(client, user_factory):
    _mock_book_detail()
    user = user_factory(username="kisaince", email="kisaince@example.com")
    response = client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL45804W", "body": "ab"},
        headers=auth_headers(user),
    )
    assert response.status_code == 422


@respx.mock
def test_upsert_emits_log_changed_event(client, user_factory, monkeypatch):
    _mock_book_detail()
    received = []
    monkeypatch.setattr(
        "app.modules.library.service.events.emit",
        lambda event, **payload: received.append((event, payload)),
    )
    user = user_factory(username="olayci", email="olayci@example.com")
    client.put("/api/v1/library/book/OL45804W", json={"rating": 9}, headers=auth_headers(user))

    assert any(event == "library.log_changed" for event, _ in received)
