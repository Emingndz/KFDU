import json
from pathlib import Path

import respx
from httpx import Response

from app.core.config import settings

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@respx.mock
def test_search_pagination_returns_page_shape(client):
    respx.get("https://openlibrary.org/search.json").mock(
        return_value=Response(200, json=_load("ol_search.json"))
    )
    response = client.get("/api/v1/catalog/search", params={"q": "sefiller", "type": "book", "page": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert len(body["items"]) > 0
    assert body["total"] >= len(body["items"])


@respx.mock
def test_detail_upserts_and_second_call_skips_http(client):
    search_route = respx.get(
        "https://openlibrary.org/search.json", params={"q": 'key:"/works/OL45804W"'}
    ).mock(return_value=Response(200, json=_load("ol_search_key_OL45804W.json")))
    work_route = respx.get("https://openlibrary.org/works/OL45804W.json").mock(
        return_value=Response(200, json=_load("ol_work_OL45804W.json"))
    )

    first = client.get("/api/v1/catalog/book/OL45804W")
    assert first.status_code == 200
    assert first.json()["title"] == "Fantastic Mr Fox"
    assert search_route.call_count == 1
    assert work_route.call_count == 1

    second = client.get("/api/v1/catalog/book/OL45804W")
    assert second.status_code == 200
    assert search_route.call_count == 1
    assert work_route.call_count == 1


@respx.mock
def test_external_service_error_returns_502(client):
    respx.get("https://openlibrary.org/search.json").mock(return_value=Response(500))
    response = client.get("/api/v1/catalog/search", params={"q": "test", "type": "book", "page": 1})
    assert response.status_code == 502
    assert response.json()["code"] == "EXTERNAL_SERVICE_ERROR"


def test_tmdb_without_key_returns_503(client):
    assert settings.TMDB_API_KEY == ""
    response = client.get("/api/v1/catalog/movie/27205")
    assert response.status_code == 503
    assert response.json()["code"] == "TMDB_NOT_CONFIGURED"


@respx.mock
def test_year_filter_with_no_matches_returns_empty_page(client):
    respx.get("https://openlibrary.org/search.json").mock(
        return_value=Response(200, json={"docs": [], "numFound": 0})
    )
    response = client.get(
        "/api/v1/catalog/discover",
        params={"type": "book", "genre": "fiction", "year_from": 1600, "year_to": 1601},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
