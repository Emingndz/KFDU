from app.core.config import settings
from app.core.errors import AppError
from app.core.http import request_json
from app.modules.catalog.schemas import ContentDetail, ContentSource, ContentSummary, Person

BASE_URL = "https://www.googleapis.com/books/v1"


def _require_key() -> str:
    if not settings.GOOGLE_BOOKS_API_KEY:
        raise AppError(404, "PROVIDER_NOT_CONFIGURED", "Bu kitap kaynağı yapılandırılmamış")
    return settings.GOOGLE_BOOKS_API_KEY


def _https(url: str | None) -> str | None:
    return url.replace("http://", "https://", 1) if url else None


def _year(published_date: str | None) -> int | None:
    return int(published_date[:4]) if published_date and published_date[:4].isdigit() else None


def to_summary(item: dict) -> ContentSummary:
    info = item.get("volumeInfo", {})
    rating = info.get("averageRating")
    return ContentSummary(
        id=None,
        type="book",
        source=ContentSource.GOOGLE_BOOKS,
        external_id=item["id"],
        title=info.get("title", ""),
        original_title=None,
        year=_year(info.get("publishedDate")),
        poster_url=_https(info.get("imageLinks", {}).get("thumbnail")),
        genres=[],
        external_rating=(rating * 2) if rating else None,
        creators=info.get("authors") or [],
    )


def to_detail(item: dict) -> ContentDetail:
    info = item.get("volumeInfo", {})
    summary = to_summary(item)
    isbn = [i["identifier"] for i in info.get("industryIdentifiers", []) if "identifier" in i]

    return ContentDetail(
        **summary.model_dump(),
        backdrop_url=None,
        overview=info.get("description"),
        runtime_minutes=None,
        page_count=info.get("pageCount"),
        seasons=None,
        original_language=info.get("language"),
        genres_detail=[],
        directors=[],
        authors=[Person(name=n) for n in (info.get("authors") or [])],
        cast=[],
        trailer_key=None,
        external_votes=info.get("ratingsCount"),
        isbn=isbn,
        external_url=info.get("infoLink"),
    )


def search(query: str, page: int, page_size: int = 20) -> tuple[list[ContentSummary], int]:
    start_index = (page - 1) * page_size
    data = request_json(
        "GET",
        f"{BASE_URL}/volumes",
        params={"q": query, "startIndex": start_index, "maxResults": page_size, "key": _require_key()},
        service="Google Books",
    )
    items = data.get("items", [])
    return [to_summary(i) for i in items], data.get("totalItems", len(items))


def detail(external_id: str) -> ContentDetail:
    item = request_json(
        "GET", f"{BASE_URL}/volumes/{external_id}", params={"key": _require_key()}, service="Google Books"
    )
    return to_detail(item)
