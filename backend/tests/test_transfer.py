import csv
import io
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import respx
from httpx import Response
from sqlalchemy import func, select

from app.core import http as http_module
from app.core.config import settings
from app.core.errors import AppError
from app.modules.library.models import LibraryEntry
from app.modules.social.models import Activity
from app.modules.transfer import service as transfer_service
from app.modules.transfer.models import ImportJob
from app.modules.transfer.parsers import ImportRow, parse_goodreads, parse_letterboxd
from app.modules.transfer.schemas import ImportFileKind
from tests.conftest import auth_headers

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _fast_import(monkeypatch):
    # Gerçekte saniyede 3 dış istek; testte beklemeye gerek yok
    monkeypatch.setattr(transfer_service, "IMPORT_REQUESTS_PER_SECOND", 10_000.0)


def _mock_book(external_id: str, title: str) -> None:
    respx.get("https://openlibrary.org/search.json", params={"q": f'key:"/works/{external_id}"'}).mock(
        return_value=Response(200, json={"docs": [{"key": f"/works/{external_id}", "title": title}]})
    )
    respx.get(f"https://openlibrary.org/works/{external_id}.json").mock(
        return_value=Response(200, json={"title": title, "description": "test"})
    )


def _mock_inception() -> None:
    respx.get(
        "https://api.themoviedb.org/3/search/movie", params={"query": "Inception", "year": "2010"}
    ).mock(
        return_value=Response(
            200, json={"results": [{"id": 27205, "title": "Inception", "release_date": "2010-07-16"}]}
        )
    )
    respx.get("https://api.themoviedb.org/3/movie/27205").mock(
        return_value=Response(200, json=_load("tmdb_movie_detail_27205.json"))
    )


def _upload(client, headers: dict, *, source: str, filename: str, text: str):
    return client.post(
        "/api/v1/users/me/import",
        headers=headers,
        data={"source": source},
        files={"file": (filename, text.encode("utf-8"), "text/csv")},
    )


def _job(client, headers: dict, job_id: int) -> dict:
    response = client.get(f"/api/v1/users/me/import/{job_id}", headers=headers)
    assert response.status_code == 200
    return response.json()


# --- Ayrıştırıcılar ---


def test_parse_letterboxd_ratings_converts_half_stars_and_keeps_dates():
    parsed = parse_letterboxd(
        (
            b"Date,Name,Year,Letterboxd URI,Rating\n"
            b"2024-01-15,Inception,2010,https://boxd.it/a,4.5\n"
            b"2023-06-01,Cats,2019,https://boxd.it/b,0.5\n"
        ),
        "ratings.csv",
    )
    assert parsed.kind == ImportFileKind.RATINGS
    inception, cats = parsed.rows
    assert (inception.title, inception.year, inception.rating, inception.status) == (
        "Inception",
        2010,
        9,
        "completed",
    )
    assert inception.finished_on == date(2024, 1, 15)
    assert inception.logged_on == date(2024, 1, 15)
    assert cats.rating == 1
    assert inception.label == "Inception (2010)"


def test_parse_letterboxd_tells_watchlist_from_watched_by_filename():
    text = b"Date,Name,Year,Letterboxd URI\n2024-02-01,The Dark Knight,2008,https://boxd.it/c\n"

    watched = parse_letterboxd(text, "watched.csv")
    assert watched.kind == ImportFileKind.WATCHED
    assert watched.rows[0].status == "completed"
    assert watched.rows[0].finished_on == date(2024, 2, 1)

    watchlist = parse_letterboxd(text, "watchlist.csv")
    assert watchlist.kind == ImportFileKind.WATCHLIST
    assert watchlist.rows[0].status == "planned"
    assert watchlist.rows[0].finished_on is None
    assert watchlist.rows[0].logged_on == date(2024, 2, 1)


def test_parse_letterboxd_diary_keeps_latest_rewatch_and_earlier_rating():
    parsed = parse_letterboxd(
        (
            b"Date,Name,Year,Letterboxd URI,Rating,Rewatch,Tags,Watched Date\n"
            b"2023-05-02,Heat,1995,https://boxd.it/d,4,,,2023-05-01\n"
            b"2024-02-03,Heat,1995,https://boxd.it/e,,Yes,,2024-02-01\n"
        ),
        "diary.csv",
    )
    assert parsed.kind == ImportFileKind.DIARY
    assert len(parsed.rows) == 1
    assert parsed.rows[0].finished_on == date(2024, 2, 1)
    assert parsed.rows[0].rating == 8


def test_parse_goodreads_maps_shelves_ratings_isbns_and_series_titles():
    parsed = parse_goodreads(
        (
            "Book Id,Title,Author,ISBN,ISBN13,My Rating,Date Read,Date Added,Exclusive Shelf\n"
            '1,"Dune (Dune, #1)",Frank Herbert,="0441172717",="9780441172719",5,2024/03/10,2024/01/02,read\n'
            '2,Ready Player One,Ernest Cline,="",="",0,,2023/11/20,to-read\n'
            '3,Okunan Kitap,Bir Yazar,="",="",0,,2024/04/01,currently-reading\n'
            '4,Bırakılan,Başka Yazar,="",="",2,,2024/05/01,did-not-finish\n'
            '5,Sadece Rafta,Biri,="",="",0,,2024/05/02,favorites\n'
        ).encode()
    )
    assert parsed.kind == ImportFileKind.GOODREADS_LIBRARY
    assert [row.status for row in parsed.rows] == ["completed", "planned", "in_progress", "dropped"]

    dune = parsed.rows[0]
    assert dune.title == "Dune"
    assert dune.author == "Frank Herbert"
    assert dune.isbns == ("9780441172719", "0441172717")
    assert dune.rating == 10
    assert dune.finished_on == date(2024, 3, 10)
    assert dune.logged_on == date(2024, 1, 2)
    assert dune.label == "Dune — Frank Herbert"

    to_read = parsed.rows[1]
    assert to_read.rating is None
    assert to_read.isbns == ()
    assert to_read.finished_on is None
    assert parsed.rows[3].rating == 4


@pytest.mark.parametrize(
    ("parser", "content"),
    [
        (parse_letterboxd, b"Title,Author,Exclusive Shelf\nDune,Frank Herbert,read\n"),
        (parse_goodreads, b"Date,Name,Year,Letterboxd URI\n2024-01-01,Heat,1995,x\n"),
        (parse_letterboxd, b"PK\x03\x04zip-icerigi"),
        (parse_goodreads, "Title,Exclusive Shelf\nKitap,read\n".encode("utf-16")),
    ],
)
def test_parsers_reject_files_from_the_wrong_source_or_format(parser, content):
    with pytest.raises(AppError) as exc_info:
        parser(content)
    assert exc_info.value.status_code == 422
    assert exc_info.value.code == "INVALID_IMPORT_FILE"


# --- Dışa aktarma ---


@respx.mock
def test_export_json_includes_profile_library_review_only_content_and_list_items(client, user_factory):
    _mock_book("OL9401W", "Birinci Kitap")
    _mock_book("OL9402W", "İkinci Kitap")
    user = user_factory(username="disaaktaran", email="disaaktaran@example.com")
    headers = auth_headers(user)
    client.put(
        "/api/v1/library/book/OL9401W",
        json={"status": "completed", "rating": 8, "is_favorite": True},
        headers=headers,
    )
    client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL9402W", "body": "Yalnız inceleme yazdım."},
        headers=headers,
    )
    list_id = client.post("/api/v1/lists", json={"title": "Favorilerim"}, headers=headers).json()["id"]
    client.post(
        f"/api/v1/lists/{list_id}/items",
        json={"type": "book", "external_id": "OL9401W", "note": "Mutlaka oku"},
        headers=headers,
    )

    response = client.get("/api/v1/users/me/export", params={"format": "json"}, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.headers["content-disposition"].startswith('attachment; filename="kfdu-disaaktaran-')
    body = response.json()
    assert (body["format"], body["version"]) == ("kfdu-export", 1)
    assert body["profile"]["username"] == "disaaktaran"
    assert body["library"][0]["content"] == {
        "type": "book",
        "source": "openlibrary",
        "external_id": "OL9401W",
        "title": "Birinci Kitap",
        "year": None,
    }
    assert body["library"][0]["rating"] == 8
    assert body["library"][0]["is_favorite"] is True
    assert body["reviews"][0]["content"]["external_id"] == "OL9402W"
    assert body["reviews"][0]["body"] == "Yalnız inceleme yazdım."
    assert body["lists"][0]["title"] == "Favorilerim"
    assert body["lists"][0]["items"][0]["content"]["external_id"] == "OL9401W"
    assert body["lists"][0]["items"][0]["note"] == "Mutlaka oku"


@respx.mock
def test_export_csv_has_bom_fixed_columns_and_one_row_per_content(client, user_factory):
    _mock_book("OL9411W", "=HYPERLINK(1)")
    _mock_book("OL9412W", "Sade Kitap")
    user = user_factory(username="csvaktaran", email="csvaktaran@example.com")
    headers = auth_headers(user)
    client.put("/api/v1/library/book/OL9411W", json={"status": "planned"}, headers=headers)
    client.put("/api/v1/library/book/OL9412W", json={"status": "completed", "rating": 7}, headers=headers)
    client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL9412W", "body": "-Harika, çok beğendim."},
        headers=headers,
    )

    response = client.get("/api/v1/users/me/export", params={"format": "csv"}, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"].endswith('.csv"')
    assert response.content.startswith("﻿".encode())

    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert rows[0] == list(transfer_service.CSV_COLUMNS)
    assert len(rows) == 3
    by_id = {row[4]: dict(zip(rows[0], row, strict=True)) for row in rows[1:]}
    # Formül gibi başlayan hücreler Excel'de çalışmasın diye tırnakla etkisizleştirilir
    assert by_id["OL9411W"]["title"] == "'=HYPERLINK(1)"
    assert by_id["OL9411W"]["status"] == "planned"
    assert by_id["OL9412W"]["rating"] == "7"
    assert by_id["OL9412W"]["review"] == "'-Harika, çok beğendim."
    assert by_id["OL9412W"]["finished_at"] == date.today().isoformat()


def test_export_rejects_unknown_format_and_requires_login(client, user_factory):
    user = user_factory(username="formatsiz", email="formatsiz@example.com")
    bad = client.get("/api/v1/users/me/export", params={"format": "xml"}, headers=auth_headers(user))
    assert bad.status_code == 422
    assert client.get("/api/v1/users/me/export").status_code == 401


# --- İçe aktarma ---


@respx.mock
def test_letterboxd_import_matches_movie_keeps_history_dates_and_stays_out_of_feed(
    client, db, user_factory, monkeypatch
):
    monkeypatch.setattr(settings, "TMDB_API_KEY", "test-key")
    _mock_inception()
    user = user_factory(username="filmiceaktaran", email="filmiceaktaran@example.com")
    headers = auth_headers(user)

    response = _upload(
        client,
        headers,
        source="letterboxd",
        filename="ratings.csv",
        text="Date,Name,Year,Letterboxd URI,Rating\n2024-01-15,Inception,2010,https://boxd.it/a,4.5\n",
    )
    assert response.status_code == 202
    job = _job(client, headers, response.json()["job_id"])
    assert job["status"] == "done"
    assert (job["total"], job["processed"], job["matched"]) == (1, 1, 1)
    assert job["report"] == {"file_kind": "ratings", "unmatched": []}
    assert job["finished_at"] is not None

    entry = client.get("/api/v1/library/movie/27205/state", headers=headers).json()["me"]["entry"]
    assert (entry["status"], entry["rating"], entry["finished_at"]) == ("completed", 9, "2024-01-15")

    db.expire_all()
    stored = db.scalar(select(LibraryEntry).where(LibraryEntry.user_id == user.id))
    assert stored.rated_at.date() == date(2024, 1, 15)
    assert stored.created_at.date() == date(2024, 1, 15)
    # İçe aktarma sessizdir: takipçilerin akışı yüzlerce eski kayıtla dolmaz
    assert db.scalar(select(func.count()).select_from(Activity).where(Activity.actor_id == user.id)) == 0

    # Geçmiş tarih korunduğu için içe aktarılan film 2024 istatistiğine sayılır, bu yılınkine sayılmaz
    stats_2024 = client.get(f"/api/v1/users/{user.username}/stats", params={"year": 2024}).json()
    assert stats_2024["totals"]["movies"] == 1
    this_year = client.get(f"/api/v1/users/{user.username}/stats", params={"year": date.today().year}).json()
    assert this_year["totals"]["movies"] == 0


@respx.mock
def test_goodreads_import_matches_by_isbn_then_title_author_and_reports_unmatched(client, db, user_factory):
    respx.get("https://openlibrary.org/search.json", params={"q": "isbn:9780001006904"}).mock(
        return_value=Response(200, json=_load("ol_search_key_OL45804W.json"))
    )
    respx.get("https://openlibrary.org/search.json", params={"q": 'key:"/works/OL45804W"'}).mock(
        return_value=Response(200, json=_load("ol_search_key_OL45804W.json"))
    )
    respx.get("https://openlibrary.org/works/OL45804W.json").mock(
        return_value=Response(200, json=_load("ol_work_OL45804W.json"))
    )
    respx.get(
        "https://openlibrary.org/search.json", params={"title": "Kitap İki", "author": "Yazar İki"}
    ).mock(return_value=Response(200, json={"docs": [{"key": "/works/OL9502W", "title": "Kitap İki"}]}))
    _mock_book("OL9502W", "Kitap İki")
    respx.get(
        "https://openlibrary.org/search.json", params={"title": "Bulunamayan Kitap", "author": "Bir Yazar"}
    ).mock(return_value=Response(200, json={"docs": []}))

    user = user_factory(username="kitapiceaktaran", email="kitapiceaktaran@example.com")
    headers = auth_headers(user)
    response = _upload(
        client,
        headers,
        source="goodreads",
        filename="goodreads_library_export.csv",
        text=(
            "Title,Author,ISBN13,My Rating,Date Read,Date Added,Exclusive Shelf\n"
            'Fantastic Mr Fox,Roald Dahl,="9780001006904",5,2024/03/10,2024/01/02,read\n'
            'Kitap İki,Yazar İki,="",0,,2024/02/02,to-read\n'
            'Bulunamayan Kitap,Bir Yazar,="",0,,2024/02/03,to-read\n'
        ),
    )
    assert response.status_code == 202
    job = _job(client, headers, response.json()["job_id"])
    assert job["status"] == "done"
    assert (job["total"], job["processed"], job["matched"]) == (3, 3, 2)
    assert job["report"]["file_kind"] == "goodreads_library"
    assert job["report"]["unmatched"] == ["Bulunamayan Kitap — Bir Yazar"]

    fox = client.get("/api/v1/library/book/OL45804W/state", headers=headers).json()["me"]["entry"]
    assert (fox["status"], fox["rating"], fox["finished_at"]) == ("completed", 10, "2024-03-10")
    second = client.get("/api/v1/library/book/OL9502W/state", headers=headers).json()["me"]["entry"]
    assert (second["status"], second["rating"]) == ("planned", None)


@respx.mock
def test_import_merges_without_overwriting_existing_ratings_or_downgrading_status(client, user_factory):
    _mock_book("OL9601W", "Okunmuş Kitap")
    _mock_book("OL9602W", "Planlanmış Kitap")
    for external_id, title in (("OL9601W", "Okunmuş Kitap"), ("OL9602W", "Planlanmış Kitap")):
        respx.get("https://openlibrary.org/search.json", params={"title": title}).mock(
            return_value=Response(200, json={"docs": [{"key": f"/works/{external_id}", "title": title}]})
        )
    user = user_factory(username="birlestiren", email="birlestiren@example.com")
    headers = auth_headers(user)
    client.put("/api/v1/library/book/OL9601W", json={"status": "completed", "rating": 6}, headers=headers)
    client.put("/api/v1/library/book/OL9602W", json={"status": "planned"}, headers=headers)

    response = _upload(
        client,
        headers,
        source="goodreads",
        filename="goodreads_library_export.csv",
        text=(
            "Title,Author,My Rating,Date Read,Exclusive Shelf\n"
            "Okunmuş Kitap,,5,,to-read\n"
            "Planlanmış Kitap,,4,2024/06/30,read\n"
        ),
    )
    job = _job(client, headers, response.json()["job_id"])
    assert (job["status"], job["matched"]) == ("done", 2)

    kept = client.get("/api/v1/library/book/OL9601W/state", headers=headers).json()["me"]["entry"]
    assert (kept["status"], kept["rating"]) == ("completed", 6)
    upgraded = client.get("/api/v1/library/book/OL9602W/state", headers=headers).json()["me"]["entry"]
    assert (upgraded["status"], upgraded["rating"], upgraded["finished_at"]) == ("completed", 8, "2024-06-30")


@respx.mock
def test_import_stops_with_clear_error_when_source_keeps_failing(client, user_factory, monkeypatch):
    monkeypatch.setattr(http_module.time, "sleep", lambda _seconds: None)
    respx.get("https://openlibrary.org/search.json").mock(return_value=Response(500))
    user = user_factory(username="kaynakcokmus", email="kaynakcokmus@example.com")
    headers = auth_headers(user)
    rows = "".join(f"Kitap {i},Yazar,0,to-read\n" for i in range(8))

    response = _upload(
        client,
        headers,
        source="goodreads",
        filename="goodreads_library_export.csv",
        text="Title,Author,My Rating,Exclusive Shelf\n" + rows,
    )
    job = _job(client, headers, response.json()["job_id"])
    assert job["status"] == "failed"
    assert "yanıt vermiyor" in job["error"]
    assert job["processed"] == transfer_service.MAX_CONSECUTIVE_ERRORS
    assert len(job["report"]["unmatched"]) == transfer_service.MAX_CONSECUTIVE_ERRORS


@respx.mock
def test_unexpected_error_marks_job_failed_instead_of_leaving_it_running(client, user_factory, monkeypatch):
    respx.get("https://openlibrary.org/search.json", params={"title": "Kitap"}).mock(
        return_value=Response(200, json={"docs": [{"key": "/works/OL9701W", "title": "Kitap"}]})
    )

    def _boom(*_args, **_kwargs):
        raise RuntimeError("beklenmedik")

    monkeypatch.setattr(transfer_service, "_apply_row", _boom)
    user = user_factory(username="patlayanis", email="patlayanis@example.com")
    headers = auth_headers(user)

    response = _upload(
        client,
        headers,
        source="goodreads",
        filename="goodreads_library_export.csv",
        text="Title,Exclusive Shelf\nKitap,read\n",
    )
    job = _job(client, headers, response.json()["job_id"])
    assert job["status"] == "failed"
    assert job["error"]
    assert job["finished_at"] is not None


def test_slow_imports_save_progress_every_few_seconds_not_only_every_ten_rows(db, user_factory, monkeypatch):
    user = user_factory(username="yavasis", email="yavasis@example.com")
    job = ImportJob(
        user_id=user.id,
        source="goodreads",
        status="running",
        total=4,
        report={"file_kind": "goodreads_library", "unmatched": []},
    )
    db.add(job)
    db.commit()

    clock = {"now": 0.0}
    seen_progress: list[int] = []

    def slow_match(_row: ImportRow) -> None:
        seen_progress.append(job.processed)
        clock["now"] += 5  # her satır 5 sn sürüyor (yavaş dış servis)

    monkeypatch.setattr(transfer_service, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(transfer_service, "_matcher", lambda _source: ("book", slow_match))

    transfer_service._process_rows(
        db, job=job, user=user, rows=[ImportRow(title=f"Kitap {i}") for i in range(4)]
    )
    assert seen_progress == [0, 1, 2, 3]
    assert (job.processed, job.matched, len(job.report["unmatched"])) == (4, 0, 4)


def test_import_rejects_second_job_while_one_is_running_but_recovers_stale_jobs(client, db, user_factory):
    user = user_factory(username="tekseferde", email="tekseferde@example.com")
    headers = auth_headers(user)
    running = ImportJob(user_id=user.id, source="goodreads", status="running", total=10)
    db.add(running)
    db.commit()

    text = "Title,Exclusive Shelf\nKitap,read\n"
    blocked = _upload(client, headers, source="goodreads", filename="g.csv", text=text)
    assert blocked.status_code == 409
    assert blocked.json()["code"] == "IMPORT_IN_PROGRESS"

    # Sunucu yeniden başlarsa iş yarıda kalır; uzun süre ilerleme yazmamış iş ölü sayılır
    running.updated_at = datetime.now(UTC) - transfer_service.STALE_JOB_AFTER - timedelta(minutes=1)
    db.commit()
    stale = _job(client, headers, running.id)
    assert stale["status"] == "failed"
    assert stale["error"]


def test_import_validates_source_file_size_content_and_tmdb_availability(client, user_factory, monkeypatch):
    user = user_factory(username="dogrulayan", email="dogrulayan@example.com")
    headers = auth_headers(user)

    unknown = _upload(client, headers, source="imdb", filename="x.csv", text="a,b\n1,2\n")
    assert unknown.status_code == 422
    assert unknown.json()["code"] == "VALIDATION_ERROR"

    wrong = _upload(
        client,
        headers,
        source="goodreads",
        filename="ratings.csv",
        text="Date,Name,Year\n2024-01-01,Heat,1995\n",
    )
    assert wrong.status_code == 422
    assert wrong.json()["code"] == "INVALID_IMPORT_FILE"

    empty = _upload(client, headers, source="goodreads", filename="g.csv", text="Title,Exclusive Shelf\n")
    assert empty.status_code == 422
    assert empty.json()["code"] == "EMPTY_IMPORT_FILE"

    assert settings.TMDB_API_KEY == ""
    no_tmdb = _upload(client, headers, source="letterboxd", filename="watched.csv", text="Date,Name,Year\n")
    assert no_tmdb.status_code == 503
    assert no_tmdb.json()["code"] == "TMDB_NOT_CONFIGURED"

    monkeypatch.setattr(transfer_service, "MAX_IMPORT_FILE_BYTES", 10)
    too_big = _upload(
        client, headers, source="goodreads", filename="g.csv", text="Title,Exclusive Shelf\nKitap,read\n"
    )
    assert too_big.status_code == 422
    assert too_big.json()["code"] == "FILE_TOO_LARGE"


def test_import_job_of_another_user_is_not_visible(client, db, user_factory):
    owner = user_factory(username="isunsahibi", email="isunsahibi@example.com")
    stranger = user_factory(username="isunyabancisi", email="isunyabancisi@example.com")
    job = ImportJob(user_id=owner.id, source="goodreads", status="done", total=1)
    db.add(job)
    db.commit()

    assert client.get(f"/api/v1/users/me/import/{job.id}", headers=auth_headers(owner)).status_code == 200
    assert client.get(f"/api/v1/users/me/import/{job.id}", headers=auth_headers(stranger)).status_code == 404


# --- core/http: içe aktarma hız sınırı ---


def test_throttle_spaces_out_consecutive_calls():
    clock = {"now": 100.0}
    sleeps: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleeps.append(round(seconds, 3))
        clock["now"] += seconds

    throttle = http_module._Throttle(2, clock=lambda: clock["now"], sleep=fake_sleep)
    throttle.wait()
    throttle.wait()
    clock["now"] += 0.2
    throttle.wait()
    clock["now"] += 5
    throttle.wait()
    assert sleeps == [0.5, 0.3]


@respx.mock
def test_throttled_block_only_slows_requests_inside_it(monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(http_module._Throttle, "wait", lambda self: calls.append(1))
    respx.get("https://example.org/a").mock(return_value=Response(200, json={}))

    http_module.request_json("GET", "https://example.org/a")
    with http_module.throttled(3):
        http_module.request_json("GET", "https://example.org/a")
        http_module.request_json("GET", "https://example.org/a")
    http_module.request_json("GET", "https://example.org/a")
    assert len(calls) == 2
