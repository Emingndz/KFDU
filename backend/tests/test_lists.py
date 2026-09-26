import json
from pathlib import Path

import respx
from httpx import Response

from app.modules.social.models import Activity
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


def test_list_crud(client, user_factory):
    user = user_factory(username="listeci", email="listeci@example.com")
    headers = auth_headers(user)

    create = client.post(
        "/api/v1/lists", json={"title": "Favori Filmlerim", "is_public": True}, headers=headers
    )
    assert create.status_code == 201
    list_id = create.json()["id"]

    detail = client.get(f"/api/v1/lists/{list_id}")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Favori Filmlerim"
    assert detail.json()["items"] == []

    update = client.patch(f"/api/v1/lists/{list_id}", json={"title": "Güncellenmiş Başlık"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["title"] == "Güncellenmiş Başlık"

    delete = client.delete(f"/api/v1/lists/{list_id}", headers=headers)
    assert delete.status_code == 204
    assert client.get(f"/api/v1/lists/{list_id}").status_code == 404


def test_adding_item_to_others_list_returns_403(client, user_factory):
    owner = user_factory(username="listesahibi", email="listesahibi@example.com")
    other = user_factory(username="listeyabanci", email="listeyabanci@example.com")

    create = client.post("/api/v1/lists", json={"title": "Sahibin Listesi"}, headers=auth_headers(owner))
    list_id = create.json()["id"]

    response = client.post(
        f"/api/v1/lists/{list_id}/items",
        json={"type": "book", "external_id": "OL45804W"},
        headers=auth_headers(other),
    )
    assert response.status_code == 403


def test_private_list_returns_404_to_others(client, user_factory):
    owner = user_factory(username="gizliliste", email="gizliliste@example.com")
    other = user_factory(username="gizliyabanci", email="gizliyabanci@example.com")

    create = client.post(
        "/api/v1/lists", json={"title": "Gizli Liste", "is_public": False}, headers=auth_headers(owner)
    )
    list_id = create.json()["id"]

    anon = client.get(f"/api/v1/lists/{list_id}")
    assert anon.status_code == 404

    stranger = client.get(f"/api/v1/lists/{list_id}", headers=auth_headers(other))
    assert stranger.status_code == 404

    owner_view = client.get(f"/api/v1/lists/{list_id}", headers=auth_headers(owner))
    assert owner_view.status_code == 200


@respx.mock
def test_reorder_items(client, user_factory):
    user = user_factory(username="siralayan", email="siralayan@example.com")
    headers = auth_headers(user)
    create = client.post("/api/v1/lists", json={"title": "Sıralama Testi"}, headers=headers)
    list_id = create.json()["id"]

    content_ids = []
    for i in range(3):
        external_id = f"OL{3000 + i}W"
        respx.get("https://openlibrary.org/search.json", params={"q": f'key:"/works/{external_id}"'}).mock(
            return_value=Response(
                200, json={"docs": [{"key": f"/works/{external_id}", "title": f"Kitap {i}"}]}
            )
        )
        respx.get(f"https://openlibrary.org/works/{external_id}.json").mock(
            return_value=Response(200, json={"title": f"Kitap {i}", "description": "test"})
        )
        add = client.post(
            f"/api/v1/lists/{list_id}/items",
            json={"type": "book", "external_id": external_id},
            headers=headers,
        )
        content_ids.append(add.json()["content"]["id"])

    reordered = list(reversed(content_ids))
    reorder_response = client.put(
        f"/api/v1/lists/{list_id}/order", json={"content_ids": reordered}, headers=headers
    )
    assert reorder_response.status_code == 204

    detail = client.get(f"/api/v1/lists/{list_id}", headers=headers).json()
    ordered_content_ids = [item["content"]["id"] for item in detail["items"]]
    assert ordered_content_ids == reordered

    bad_reorder = client.put(
        f"/api/v1/lists/{list_id}/order", json={"content_ids": content_ids[:-1]}, headers=headers
    )
    assert bad_reorder.status_code == 400


@respx.mock
def test_adding_item_to_public_list_creates_activity_and_removed_on_private(client, db, user_factory):
    _mock_book_detail()
    user = user_factory(username="aktiviteliste", email="aktiviteliste@example.com")
    headers = auth_headers(user)

    create = client.post("/api/v1/lists", json={"title": "Herkese Açık", "is_public": True}, headers=headers)
    list_id = create.json()["id"]
    assert db.query(Activity).filter_by(verb="list_create", list_id=list_id).count() == 1

    client.post(
        f"/api/v1/lists/{list_id}/items", json={"type": "book", "external_id": "OL45804W"}, headers=headers
    )
    assert db.query(Activity).filter_by(verb="list_add", list_id=list_id).count() == 1

    client.patch(f"/api/v1/lists/{list_id}", json={"is_public": False}, headers=headers)
    assert db.query(Activity).filter_by(list_id=list_id).count() == 0


@respx.mock
def test_my_lists_contains_flag(client, user_factory):
    _mock_book_detail()
    respx.get("https://openlibrary.org/search.json", params={"q": 'key:"/works/OL00000W"'}).mock(
        return_value=Response(200, json={"docs": [{"key": "/works/OL00000W", "title": "Bilinmeyen"}]})
    )
    respx.get("https://openlibrary.org/works/OL00000W.json").mock(
        return_value=Response(200, json={"title": "Bilinmeyen", "description": "test"})
    )
    user = user_factory(username="icerirmi", email="icerirmi@example.com")
    headers = auth_headers(user)

    create = client.post("/api/v1/lists", json={"title": "Test Listesi"}, headers=headers)
    list_id = create.json()["id"]
    client.post(
        f"/api/v1/lists/{list_id}/items", json={"type": "book", "external_id": "OL45804W"}, headers=headers
    )

    response = client.get(
        "/api/v1/lists/mine", params={"type": "book", "external_id": "OL45804W"}, headers=headers
    )
    assert response.status_code == 200
    matched = next(item for item in response.json() if item["id"] == list_id)
    assert matched["contains"] is True

    response_missing = client.get(
        "/api/v1/lists/mine", params={"type": "book", "external_id": "OL00000W"}, headers=headers
    )
    matched_missing = next(item for item in response_missing.json() if item["id"] == list_id)
    assert matched_missing["contains"] is False
