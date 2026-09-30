import difflib
import re

from app.core.http import request_json
from app.modules.catalog import genres as genre_utils
from app.modules.catalog.schemas import (
    AuthorDetail,
    AuthorWork,
    ContentDetail,
    ContentSource,
    ContentSummary,
    Person,
)

BASE_URL = "https://openlibrary.org"
COVERS_BASE = "https://covers.openlibrary.org"

_YEAR_RE = re.compile(r"\d{4}")

_LANGUAGE_MAP = {"tur": "tr", "eng": "en"}

_SEARCH_FIELDS = (
    "key,title,subtitle,author_name,author_key,first_publish_year,cover_i,"
    "number_of_pages_median,ratings_average,ratings_count,subject,language,edition_count,isbn"
)

_SORT_MAP = {"popular": "readinglog", "rating": "rating", "newest": "new", "oldest": "old"}


def _external_id(key: str) -> str:
    return key.rsplit("/", 1)[-1]


def _cover_url(cover_i: int | None, size: str) -> str | None:
    return f"{COVERS_BASE}/b/id/{cover_i}-{size}.jpg" if cover_i else None


def _language(codes: list[str] | None) -> str | None:
    if not codes:
        return None
    code = codes[0]
    return _LANGUAGE_MAP.get(code, code if len(code) == 2 else None)


def _extract_description(value: object) -> str | None:
    if isinstance(value, dict):
        return value.get("value")
    return value if isinstance(value, str) else None


def _extract_year(value: str | None) -> int | None:
    if not value:
        return None
    match = _YEAR_RE.search(value)
    return int(match.group()) if match else None


def to_summary(doc: dict) -> ContentSummary:
    ratings_average = doc.get("ratings_average")
    return ContentSummary(
        id=None,
        type="book",
        source=ContentSource.OPENLIBRARY,
        external_id=_external_id(doc["key"]),
        title=doc.get("title", ""),
        original_title=None,
        year=doc.get("first_publish_year"),
        poster_url=_cover_url(doc.get("cover_i"), "M"),
        genres=genre_utils.from_ol_subjects(doc.get("subject") or []),
        external_rating=(ratings_average * 2) if ratings_average else None,
        creators=doc.get("author_name") or [],
    )


def search(query: str, page: int, limit: int = 20) -> tuple[list[ContentSummary], int]:
    data = request_json(
        "GET",
        f"{BASE_URL}/search.json",
        params={"q": query, "page": page, "limit": limit, "fields": _SEARCH_FIELDS},
        service="Open Library",
    )
    docs = data.get("docs", [])
    return [to_summary(d) for d in docs], data.get("numFound", len(docs))


def discover(
    *,
    subject: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    sort: str = "rating",
    language: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[ContentSummary], int]:
    query_parts = [f"subject:{subject}"] if subject else []
    if year_from or year_to:
        query_parts.append(f"first_publish_year:[{year_from or '*'} TO {year_to or '*'}]")
    if language == "tr":
        query_parts.append("language:tur")
    if min_rating:
        query_parts.append(f"ratings_average:[{min_rating / 2} TO 5]")

    data = request_json(
        "GET",
        f"{BASE_URL}/search.json",
        params={
            "q": " ".join(query_parts),
            "page": page,
            "limit": limit,
            "fields": _SEARCH_FIELDS,
            "sort": _SORT_MAP.get(sort, sort),
        },
        service="Open Library",
    )
    docs = data.get("docs", [])
    items = [to_summary(d) for d in docs]
    if min_rating:
        items = [i for i in items if i.external_rating is not None and i.external_rating >= min_rating]
    return items, data.get("numFound", len(items))


def trending(limit: int = 20) -> list[ContentSummary]:
    data = request_json(
        "GET", f"{BASE_URL}/trending/weekly.json", params={"limit": limit}, service="Open Library"
    )
    return [to_summary(w) for w in data.get("works", [])]


def detail(external_id: str) -> ContentDetail:
    search_data = request_json(
        "GET",
        f"{BASE_URL}/search.json",
        params={"q": f'key:"/works/{external_id}"', "fields": _SEARCH_FIELDS},
        service="Open Library",
    )
    docs = search_data.get("docs", [])
    doc = docs[0] if docs else {"key": f"/works/{external_id}", "title": external_id}
    summary = to_summary(doc)

    work = request_json("GET", f"{BASE_URL}/works/{external_id}.json", service="Open Library")

    author_keys = doc.get("author_key") or []
    author_names = doc.get("author_name") or []
    authors = [Person(id=key, name=name) for key, name in zip(author_keys, author_names, strict=False)]

    return ContentDetail(
        **summary.model_dump(),
        backdrop_url=None,
        overview=_extract_description(work.get("description")),
        runtime_minutes=None,
        page_count=doc.get("number_of_pages_median"),
        seasons=None,
        original_language=_language(doc.get("language")),
        genres_detail=[],
        directors=[],
        authors=authors,
        cast=[],
        trailer_key=None,
        external_votes=doc.get("ratings_count"),
        isbn=doc.get("isbn") or [],
        external_url=f"https://openlibrary.org/works/{external_id}",
    )


def similar(external_id: str) -> list[ContentSummary]:
    detail_data = detail(external_id)
    results: list[ContentSummary] = []
    if detail_data.authors:
        author_key = detail_data.authors[0].id
        if author_key:
            data = request_json(
                "GET",
                f"{BASE_URL}/search.json",
                params={"q": f"author_key:{author_key}", "limit": 10, "fields": _SEARCH_FIELDS},
                service="Open Library",
            )
            results = [to_summary(d) for d in data.get("docs", []) if _external_id(d["key"]) != external_id]
    if len(results) < 5 and detail_data.genres:
        subject = genre_utils.to_ol_subject(detail_data.genres[0])
        if subject:
            data = request_json(
                "GET",
                f"{BASE_URL}/search.json",
                params={
                    "q": f"subject:{subject}",
                    "sort": "rating",
                    "limit": 10,
                    "fields": _SEARCH_FIELDS,
                },
                service="Open Library",
            )
            existing_ids = {r.external_id for r in results} | {external_id}
            results += [
                to_summary(d) for d in data.get("docs", []) if _external_id(d["key"]) not in existing_ids
            ]
    return results[:10]


def to_author_detail(raw: dict, works_data: dict) -> AuthorDetail:
    works = []
    for entry in works_data.get("entries", []):
        covers = entry.get("covers") or []
        cover_id = covers[0] if covers and covers[0] > 0 else None
        works.append(
            AuthorWork(
                external_id=_external_id(entry["key"]),
                title=entry.get("title", ""),
                poster_url=_cover_url(cover_id, "M"),
                year=_extract_year(entry.get("first_publish_date")),
            )
        )
    works.sort(key=lambda w: w.year or 0, reverse=True)

    photos = raw.get("photos") or []
    photo_id = photos[0] if photos and photos[0] > 0 else None

    return AuthorDetail(
        id=_external_id(raw.get("key", "")),
        name=raw.get("name", ""),
        photo_url=f"{COVERS_BASE}/a/id/{photo_id}-M.jpg" if photo_id else None,
        biography=_extract_description(raw.get("bio")),
        birth_date=raw.get("birth_date"),
        death_date=raw.get("death_date"),
        works=works,
    )


def author(author_id: str) -> AuthorDetail:
    raw = request_json("GET", f"{BASE_URL}/authors/{author_id}.json", service="Open Library")
    works_data = request_json(
        "GET", f"{BASE_URL}/authors/{author_id}/works.json", params={"limit": 50}, service="Open Library"
    )
    return to_author_detail(raw, works_data)


def find_source_book(title: str, author: str | None) -> ContentSummary | None:
    params = {"title": title, "fields": _SEARCH_FIELDS, "limit": 5}
    if author:
        params["author"] = author
    data = request_json("GET", f"{BASE_URL}/search.json", params=params, service="Open Library")
    docs = data.get("docs", [])
    if not docs:
        return None

    target = genre_utils.normalize_title(title)
    best_doc, best_score = None, 0.0
    for doc in docs:
        candidate = genre_utils.normalize_title(doc.get("title", ""))
        score = difflib.SequenceMatcher(None, target, candidate).ratio()
        if score > best_score:
            best_score, best_doc = score, doc

    return to_summary(best_doc) if best_doc is not None and best_score >= 0.6 else None
