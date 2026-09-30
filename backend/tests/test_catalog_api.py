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


def test_tmdb_tv_without_key_returns_503(client):
    assert settings.TMDB_API_KEY == ""
    response = client.get("/api/v1/catalog/tv/1396")
    assert response.status_code == 503
    assert response.json()["code"] == "TMDB_NOT_CONFIGURED"


def test_people_without_key_returns_503(client):
    assert settings.TMDB_API_KEY == ""
    response = client.get("/api/v1/catalog/people/525")
    assert response.status_code == 503
    assert response.json()["code"] == "TMDB_NOT_CONFIGURED"


@respx.mock
def test_author_detail_endpoint_returns_normalized_data(client):
    respx.get("https://openlibrary.org/authors/OL34184A.json").mock(
        return_value=Response(200, json=_load("ol_author_OL34184A.json"))
    )
    respx.get("https://openlibrary.org/authors/OL34184A/works.json").mock(
        return_value=Response(200, json=_load("ol_author_works_OL34184A.json"))
    )
    response = client.get("/api/v1/catalog/authors/OL34184A")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Roald Dahl"
    assert [w["title"] for w in body["works"]] == ["Matilda", "Fantastic Mr Fox", "Eski Bir Eser"]


@respx.mock
def test_book_adaptations_matches_by_keyword_and_by_novel_author(client, monkeypatch):
    monkeypatch.setattr(settings, "TMDB_API_KEY", "test-key")
    respx.get("https://openlibrary.org/search.json", params={"q": 'key:"/works/OL45804W"'}).mock(
        return_value=Response(200, json=_load("ol_search_key_OL45804W.json"))
    )
    respx.get("https://openlibrary.org/works/OL45804W.json").mock(
        return_value=Response(200, json=_load("ol_work_OL45804W.json"))
    )

    respx.get("https://api.themoviedb.org/3/search/movie").mock(
        return_value=Response(
            200,
            json={
                "results": [
                    {"id": 9075, "title": "Fantastic Mr. Fox", "release_date": "2009-11-13"},
                    {"id": 9076, "title": "Fantastic Mr. Fox 2", "release_date": "2015-01-01"},
                ]
            },
        )
    )
    respx.get("https://api.themoviedb.org/3/search/tv").mock(
        return_value=Response(200, json={"results": [{"id": 999, "name": "Tamamen Alakasız Dizi"}]})
    )
    respx.get("https://api.themoviedb.org/3/movie/9075").mock(
        return_value=Response(
            200,
            json={"credits": {"crew": [{"name": "Roald Dahl", "job": "Novel"}]}, "keywords": {"keywords": []}},
        )
    )
    respx.get("https://api.themoviedb.org/3/movie/9076").mock(
        return_value=Response(
            200,
            json={"credits": {"crew": []}, "keywords": {"keywords": [{"id": 818, "name": "based on novel"}]}},
        )
    )

    response = client.get("/api/v1/catalog/book/OL45804W/adaptations")
    assert response.status_code == 200
    assert [item["external_id"] for item in response.json()] == ["9075", "9076"]


@respx.mock
def test_movie_without_novel_credit_has_no_source_book(client, monkeypatch):
    monkeypatch.setattr(settings, "TMDB_API_KEY", "test-key")
    respx.get("https://api.themoviedb.org/3/movie/27205").mock(
        return_value=Response(200, json=_load("tmdb_movie_detail_27205.json"))
    )
    response = client.get("/api/v1/catalog/movie/27205/source-book")
    assert response.status_code == 404


@respx.mock
def test_movie_source_book_endpoint_finds_matching_open_library_book(client, monkeypatch):
    monkeypatch.setattr(settings, "TMDB_API_KEY", "test-key")
    respx.get("https://api.themoviedb.org/3/movie/438631").mock(
        return_value=Response(200, json=_load("tmdb_movie_detail_438631.json"))
    )
    respx.get("https://openlibrary.org/search.json", params={"title": "Dune", "author": "Frank Herbert"}).mock(
        return_value=Response(
            200, json={"docs": [{"key": "/works/OL893415W", "title": "Dune", "author_name": ["Frank Herbert"]}]}
        )
    )
    response = client.get("/api/v1/catalog/movie/438631/source-book")
    assert response.status_code == 200
    assert response.json()["external_id"] == "OL893415W"


def test_tv_genres_work_without_tmdb_key(client):
    response = client.get("/api/v1/catalog/genres", params={"type": "tv"})
    assert response.status_code == 200
    keys = {g["key"] for g in response.json()}
    assert "action" in keys and "children" in keys
    assert "horror" not in keys


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
