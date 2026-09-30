import json
from pathlib import Path

from app.modules.catalog.providers import openlibrary, tmdb

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_tmdb_movie_detail_normalizes_director_runtime_and_genres():
    raw = _load("tmdb_movie_detail_27205.json")
    detail = tmdb.to_detail(raw, "movie")

    assert detail.directors[0].name == "Christopher Nolan"
    assert detail.runtime_minutes == 148
    assert set(detail.genres) == {"action", "science_fiction", "adventure"}
    assert detail.trailer_key == "YoHD9XEInc0"
    assert "Netflix" in detail.providers.flatrate
    assert detail.cast[0].name == "Leonardo DiCaprio"


def test_tmdb_tv_detail_uses_created_by_and_episode_runtime():
    raw = _load("tmdb_tv_detail_1396.json")
    detail = tmdb.to_detail(raw, "tv")

    assert detail.creators == ["Vince Gilligan"]
    assert detail.directors[0].name == "Vince Gilligan"
    assert detail.directors[0].role == "creator"
    assert detail.runtime_minutes == 47
    assert detail.seasons == 5
    assert set(detail.genres) == {"drama", "crime"}
    assert len(detail.seasons_detail) == 2
    assert detail.seasons_detail[0].number == 1
    assert detail.seasons_detail[0].episode_count == 7
    assert detail.seasons_detail[0].air_year == 2008
    assert detail.seasons_detail[1].name == "Sezon 2"


def test_tmdb_movie_detail_has_no_seasons():
    raw = _load("tmdb_movie_detail_27205.json")
    detail = tmdb.to_detail(raw, "movie")

    assert detail.seasons is None
    assert detail.seasons_detail == []


def test_tmdb_search_results_use_genre_ids_without_credits():
    raw = _load("tmdb_search_movie.json")
    items = [tmdb.to_summary(r, "movie") for r in raw["results"]]

    assert items[0].title == "Inception"
    assert "action" in items[0].genres
    assert items[0].creators == []


def test_openlibrary_summary_normalizes_cover_and_rating():
    raw = _load("ol_search.json")
    doc = raw["docs"][0]
    summary = openlibrary.to_summary(doc)

    assert summary.external_id == doc["key"].rsplit("/", 1)[-1]
    if doc.get("cover_i"):
        assert summary.poster_url == f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
    if doc.get("ratings_average"):
        assert summary.external_rating == doc["ratings_average"] * 2


def test_openlibrary_description_handles_string_and_dict_forms():
    assert openlibrary._extract_description("düz metin") == "düz metin"
    assert openlibrary._extract_description({"value": "sözlük içinde metin"}) == "sözlük içinde metin"
    assert openlibrary._extract_description(None) is None


def test_openlibrary_work_detail_description_is_extracted():
    work = _load("ol_work_OL45804W.json")
    assert isinstance(openlibrary._extract_description(work.get("description")), str)


def test_tmdb_person_detail_normalizes_credits_sorted_and_deduped():
    raw = _load("tmdb_person_525.json")
    detail = tmdb.to_person_detail(raw)

    assert detail.name == "Christopher Nolan"
    assert detail.known_for == "Yönetmenlik"
    assert detail.birthday == "1970-07-30"

    # 3 "Director" işli ham kredi (biri kasıtlı tekrar) -> 2 tekil sonuç, popülerliğe göre azalan.
    assert [c.title for c in detail.directing] == ["The Dark Knight", "Inception"]
    assert detail.directing[0].external_id == "155"
    assert detail.directing[0].type == "movie"

    assert [c.title for c in detail.acting] == ["Larry Crowne"]
    assert detail.acting[0].year == 2011


def test_openlibrary_author_detail_normalizes_works_sorted_by_year():
    raw = _load("ol_author_OL34184A.json")
    works_raw = _load("ol_author_works_OL34184A.json")
    detail = openlibrary.to_author_detail(raw, works_raw)

    assert detail.id == "OL34184A"
    assert detail.name == "Roald Dahl"
    assert detail.biography == "İngiliz çocuk kitabı yazarı."

    assert [w.title for w in detail.works] == ["Matilda", "Fantastic Mr Fox", "Eski Bir Eser"]
    assert detail.works[0].poster_url == "https://covers.openlibrary.org/b/id/8231990-M.jpg"
    # covers: [-1] "kapak yok" sentinel'i null'a çevrilmeli, hataya düşmemeli.
    assert detail.works[2].poster_url is None
