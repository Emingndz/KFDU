import difflib
import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cache import ttl_cache
from app.core.config import settings
from app.core.errors import AppError
from app.core.genres import GENRE_TABLE
from app.core.pagination import Page
from app.modules.catalog import genres as genre_utils
from app.modules.catalog.models import Content
from app.modules.catalog.providers import google_books, openlibrary, tmdb
from app.modules.catalog.schemas import (
    AuthorDetail,
    ContentDetail,
    ContentSummary,
    GenreOut,
    Person,
    PersonDetail,
    Providers,
    SeasonOut,
)

CONTENT_FRESHNESS = timedelta(days=7)
_OL_ID_PATTERN = re.compile(r"^OL\d+W$")


def resolve_source(content_type: str, external_id: str) -> str:
    if content_type != "book":
        return "tmdb"
    return "openlibrary" if _OL_ID_PATTERN.match(external_id) else "google_books"


def _book_provider():
    return google_books if settings.BOOK_PROVIDER == "google_books" else openlibrary


@ttl_cache(ttl=600)
def _search_cached(content_type: str, query: str, page: int) -> tuple[list[ContentSummary], int]:
    if content_type == "book":
        return _book_provider().search(query, page)
    return tmdb.search(content_type, query, page)


def search(content_type: str, query: str, page: int, page_size: int = 20) -> Page[ContentSummary]:
    items, total = _search_cached(content_type, query, page)
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


@ttl_cache(ttl=1800)
def _discover_cached(
    content_type: str,
    genre: str | None,
    year_from: int | None,
    year_to: int | None,
    min_rating: float | None,
    sort: str,
    language: str | None,
    page: int,
) -> tuple[list[ContentSummary], int]:
    if content_type == "book":
        subject = genre_utils.to_ol_subject(genre) if genre else None
        return _book_provider().discover(
            subject=subject,
            year_from=year_from,
            year_to=year_to,
            min_rating=min_rating,
            sort=sort,
            language=language,
            page=page,
        )
    return tmdb.discover(
        content_type,
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        sort=sort,
        page=page,
    )


def discover(
    content_type: str,
    *,
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    sort: str = "popular",
    language: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> Page[ContentSummary]:
    items, total = _discover_cached(content_type, genre, year_from, year_to, min_rating, sort, language, page)
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


@ttl_cache(ttl=3600)
def trending(content_type: str) -> list[ContentSummary]:
    if content_type == "book":
        return openlibrary.trending()
    return tmdb.trending(content_type)


@ttl_cache(ttl=3600)
def collection(name: str) -> list[ContentSummary]:
    return tmdb.collection(name)


@ttl_cache(ttl=21600)
def similar(content_type: str, external_id: str) -> list[ContentSummary]:
    if content_type == "book":
        return openlibrary.similar(external_id)
    return tmdb.similar(content_type, external_id)


def genres(content_type: str) -> list[GenreOut]:
    attr = {"movie": "tmdb_movie_id", "tv": "tmdb_tv_id", "book": "ol_subject"}[content_type]
    return [GenreOut(key=g.key, label=g.label) for g in GENRE_TABLE if getattr(g, attr) is not None]


@ttl_cache(ttl=21600)
def _fetch_detail(content_type: str, external_id: str) -> ContentDetail:
    if content_type == "book":
        source = resolve_source(content_type, external_id)
        provider = openlibrary if source == "openlibrary" else google_books
        return provider.detail(external_id)
    return tmdb.detail(content_type, external_id)


def _detail_to_content_fields(detail: ContentDetail) -> dict:
    return {
        "title": detail.title,
        "original_title": detail.original_title,
        "year": detail.year,
        "poster_url": detail.poster_url,
        "backdrop_url": detail.backdrop_url,
        "overview": detail.overview,
        "genres": detail.genres,
        "people": {
            "directors": [p.model_dump() for p in detail.directors],
            "authors": [p.model_dump() for p in detail.authors],
            "cast": [p.model_dump() for p in detail.cast],
        },
        "runtime_minutes": detail.runtime_minutes,
        "page_count": detail.page_count,
        "seasons": detail.seasons,
        "original_language": detail.original_language,
        "external_rating": detail.external_rating,
        "external_votes": detail.external_votes,
        "extra": {
            "trailer_key": detail.trailer_key,
            "providers": detail.providers.model_dump(),
            "isbn": detail.isbn,
            "external_url": detail.external_url,
            "seasons_detail": [s.model_dump() for s in detail.seasons_detail],
            "novel_authors": detail.novel_authors,
            "has_book_keyword": detail.has_book_keyword,
        },
        "fetched_at": datetime.now(UTC),
    }


def get_or_create_content(db: Session, content_type: str, external_id: str) -> Content:
    source = resolve_source(content_type, external_id)
    row = db.scalar(
        select(Content).where(
            Content.type == content_type, Content.source == source, Content.external_id == external_id
        )
    )
    fresh = (
        row is not None
        and row.fetched_at is not None
        and (datetime.now(UTC) - row.fetched_at) <= CONTENT_FRESHNESS
    )
    if fresh:
        return row

    detail_schema = _fetch_detail(content_type, external_id)
    payload = _detail_to_content_fields(detail_schema)

    if row is None:
        row = Content(type=content_type, source=source, external_id=external_id, **payload)
        db.add(row)
    else:
        for key, value in payload.items():
            setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


def content_to_summary(content: Content) -> ContentSummary:
    people = content.people or {}
    directors = [Person(**p) for p in people.get("directors", [])]
    authors = [Person(**p) for p in people.get("authors", [])]
    creators = [p.name for p in (directors or authors)]

    return ContentSummary(
        id=content.id,
        type=content.type,
        source=content.source,
        external_id=content.external_id,
        title=content.title,
        original_title=content.original_title,
        year=content.year,
        poster_url=content.poster_url,
        genres=content.genres or [],
        external_rating=content.external_rating,
        creators=creators,
    )


def _content_to_detail(content: Content) -> ContentDetail:
    summary = content_to_summary(content)
    people = content.people or {}
    extra = content.extra or {}
    directors = [Person(**p) for p in people.get("directors", [])]
    authors = [Person(**p) for p in people.get("authors", [])]
    cast = [Person(**p) for p in people.get("cast", [])]
    providers_data = extra.get("providers") or {}

    return ContentDetail(
        **summary.model_dump(),
        backdrop_url=content.backdrop_url,
        overview=content.overview,
        runtime_minutes=content.runtime_minutes,
        page_count=content.page_count,
        seasons=content.seasons,
        seasons_detail=[SeasonOut(**s) for s in extra.get("seasons_detail") or []],
        original_language=content.original_language,
        genres_detail=[GenreOut(key=k, label=genre_utils.label(k)) for k in (content.genres or [])],
        directors=directors,
        authors=authors,
        cast=cast,
        trailer_key=extra.get("trailer_key"),
        providers=Providers(**providers_data) if providers_data else Providers(),
        external_votes=content.external_votes,
        isbn=extra.get("isbn") or [],
        external_url=extra.get("external_url"),
        novel_authors=extra.get("novel_authors") or [],
        has_book_keyword=extra.get("has_book_keyword") or False,
    )


def get_detail(db: Session, content_type: str, external_id: str) -> ContentDetail:
    content = get_or_create_content(db, content_type, external_id)
    return _content_to_detail(content)


@ttl_cache(ttl=21600)
def get_person(person_id: str) -> PersonDetail:
    return tmdb.person(person_id)


@ttl_cache(ttl=21600)
def get_author(author_id: str) -> AuthorDetail:
    return openlibrary.author(author_id)


@ttl_cache(ttl=604800)
def _find_adaptations_cached(title: str, author: str | None) -> list[ContentSummary]:
    return tmdb.find_adaptations(title, author)


def get_book_adaptations(db: Session, external_id: str) -> list[ContentSummary]:
    detail = get_detail(db, "book", external_id)
    author = detail.authors[0].name if detail.authors else None
    return _find_adaptations_cached(detail.title, author)


@ttl_cache(ttl=604800)
def _find_source_book_cached(title: str, author: str | None) -> ContentSummary | None:
    return openlibrary.find_source_book(title, author)


def get_source_book(db: Session, content_type: str, external_id: str) -> ContentSummary | None:
    if content_type == "book":
        return None
    detail = get_detail(db, content_type, external_id)
    if not detail.novel_authors and not detail.has_book_keyword:
        return None
    author = detail.novel_authors[0] if detail.novel_authors else None
    title = detail.original_title or detail.title
    return _find_source_book_cached(title, author)


def search_best(title: str, types: list[str]) -> ContentSummary | None:
    target = genre_utils.normalize_title(title)
    best: ContentSummary | None = None
    best_score = 0.0
    for content_type in types:
        try:
            items, _ = _search_cached(content_type, title, 1)
        except AppError:
            continue
        for item in items:
            score = difflib.SequenceMatcher(None, target, genre_utils.normalize_title(item.title)).ratio()
            if score > best_score:
                best_score, best = score, item
    return best if best_score >= 0.6 else None
