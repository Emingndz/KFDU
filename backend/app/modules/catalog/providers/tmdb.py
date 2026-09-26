from app.core.config import settings
from app.core.errors import AppError
from app.core.http import request_json
from app.modules.catalog import genres as genre_utils
from app.modules.catalog.schemas import (
    ContentDetail,
    ContentSource,
    ContentSummary,
    GenreOut,
    Person,
    Providers,
)

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p"

_SORT_MAP_MOVIE = {
    "popular": "popularity.desc",
    "rating": "vote_average.desc",
    "newest": "primary_release_date.desc",
    "oldest": "primary_release_date.asc",
}
_SORT_MAP_TV = {
    "popular": "popularity.desc",
    "rating": "vote_average.desc",
    "newest": "first_air_date.desc",
    "oldest": "first_air_date.asc",
}


def _require_key() -> str:
    if not settings.TMDB_API_KEY:
        raise AppError(503, "TMDB_NOT_CONFIGURED", "Film verileri için TMDB anahtarı yapılandırılmamış")
    return settings.TMDB_API_KEY


def _params(**extra: object) -> dict:
    return {
        "api_key": _require_key(),
        "language": settings.TMDB_LANGUAGE,
        "include_adult": "false",
        **extra,
    }


def _image_url(path: str | None, size: str) -> str | None:
    return f"{IMAGE_BASE}/{size}{path}" if path else None


def _year_from_date(value: str | None) -> int | None:
    return int(value[:4]) if value and len(value) >= 4 else None


def _genre_ids(raw: dict) -> list[int]:
    if "genre_ids" in raw:
        return raw["genre_ids"]
    return [g["id"] for g in raw.get("genres", [])]


def to_summary(raw: dict, content_type: str) -> ContentSummary:
    is_movie = content_type == "movie"
    title = raw.get("title") if is_movie else raw.get("name")
    original_title = raw.get("original_title") if is_movie else raw.get("original_name")
    date_value = raw.get("release_date") if is_movie else raw.get("first_air_date")

    crew = raw.get("credits", {}).get("crew", [])
    if is_movie:
        creators = [c["name"] for c in crew if c.get("job") == "Director"]
    else:
        creators = [c.get("name", "") for c in raw.get("created_by", [])]

    return ContentSummary(
        id=None,
        type=content_type,
        source=ContentSource.TMDB,
        external_id=str(raw["id"]),
        title=title or "",
        original_title=original_title,
        year=_year_from_date(date_value),
        poster_url=_image_url(raw.get("poster_path"), "w342"),
        genres=genre_utils.from_tmdb_ids(_genre_ids(raw), content_type),
        external_rating=raw.get("vote_average"),
        creators=creators,
    )


def _pick_trailer(videos: list[dict]) -> str | None:
    candidates = [v for v in videos if v.get("site") == "YouTube" and v.get("type") == "Trailer"]
    if not candidates:
        return None

    def score(v: dict) -> tuple[int, int]:
        return (1 if v.get("official") else 0, 1 if v.get("iso_639_1") == "tr" else 0)

    return max(candidates, key=score).get("key")


def _pick_providers(region_data: dict) -> Providers:
    def names(items: list[dict]) -> list[str]:
        return [i["provider_name"] for i in items]

    return Providers(
        flatrate=names(region_data.get("flatrate", [])),
        rent=names(region_data.get("rent", [])),
        buy=names(region_data.get("buy", [])),
        link=region_data.get("link"),
    )


def to_detail(raw: dict, content_type: str) -> ContentDetail:
    summary = to_summary(raw, content_type)
    is_movie = content_type == "movie"

    crew = raw.get("credits", {}).get("crew", [])
    cast_raw = raw.get("credits", {}).get("cast", [])[:15]

    directors = [
        Person(
            id=str(c["id"]),
            name=c["name"],
            role="director",
            photo_url=_image_url(c.get("profile_path"), "w185"),
        )
        for c in crew
        if c.get("job") == "Director"
    ]
    cast = [
        Person(
            id=str(c["id"]),
            name=c["name"],
            role=c.get("character"),
            photo_url=_image_url(c.get("profile_path"), "w185"),
        )
        for c in cast_raw
    ]

    region_providers = raw.get("watch/providers", {}).get("results", {}).get(settings.TMDB_REGION, {})
    runtime = raw.get("runtime") if is_movie else next(iter(raw.get("episode_run_time") or []), None)

    return ContentDetail(
        **summary.model_dump(),
        backdrop_url=_image_url(raw.get("backdrop_path"), "w1280"),
        overview=raw.get("overview") or None,
        runtime_minutes=runtime,
        page_count=None,
        seasons=None if is_movie else raw.get("number_of_seasons"),
        original_language=raw.get("original_language"),
        genres_detail=[GenreOut(key=k, label=genre_utils.label(k)) for k in summary.genres],
        directors=directors,
        authors=[],
        cast=cast,
        trailer_key=_pick_trailer(raw.get("videos", {}).get("results", [])),
        providers=_pick_providers(region_providers),
        external_votes=raw.get("vote_count"),
        isbn=[],
        external_url=f"https://www.themoviedb.org/{content_type}/{raw['id']}",
    )


def search(content_type: str, query: str, page: int) -> tuple[list[ContentSummary], int]:
    endpoint = "search/movie" if content_type == "movie" else "search/tv"
    data = request_json(
        "GET", f"{BASE_URL}/{endpoint}", params=_params(query=query, page=page), service="TMDB"
    )
    items = [to_summary(r, content_type) for r in data.get("results", [])]
    return items, data.get("total_results", len(items))


def discover(
    content_type: str,
    *,
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    sort: str = "popular",
    page: int = 1,
) -> tuple[list[ContentSummary], int]:
    is_movie = content_type == "movie"
    endpoint = "discover/movie" if is_movie else "discover/tv"
    sort_map = _SORT_MAP_MOVIE if is_movie else _SORT_MAP_TV
    date_gte = "primary_release_date.gte" if is_movie else "first_air_date.gte"
    date_lte = "primary_release_date.lte" if is_movie else "first_air_date.lte"

    query_params = _params(page=page, sort_by=sort_map.get(sort, "popularity.desc"))
    if genre:
        tmdb_ids = genre_utils.to_tmdb_ids([genre], content_type)
        if tmdb_ids:
            query_params["with_genres"] = tmdb_ids[0]
    if year_from:
        query_params[date_gte] = f"{year_from}-01-01"
    if year_to:
        query_params[date_lte] = f"{year_to}-12-31"
    if min_rating:
        query_params["vote_average.gte"] = min_rating
        if sort == "rating":
            query_params["vote_count.gte"] = 200

    data = request_json("GET", f"{BASE_URL}/{endpoint}", params=query_params, service="TMDB")
    items = [to_summary(r, content_type) for r in data.get("results", [])]
    return items, data.get("total_results", len(items))


def trending(content_type: str) -> list[ContentSummary]:
    endpoint = "tv" if content_type == "tv" else "movie"
    data = request_json("GET", f"{BASE_URL}/trending/{endpoint}/week", params=_params(), service="TMDB")
    return [to_summary(r, content_type) for r in data.get("results", [])]


def collection(name: str) -> list[ContentSummary]:
    endpoints = {"now_playing": "movie/now_playing", "upcoming": "movie/upcoming"}
    endpoint = endpoints.get(name)
    if endpoint is None:
        raise AppError(404, "NOT_FOUND", "Bilinmeyen koleksiyon")
    data = request_json(
        "GET", f"{BASE_URL}/{endpoint}", params=_params(region=settings.TMDB_REGION), service="TMDB"
    )
    return [to_summary(r, "movie") for r in data.get("results", [])]


def detail(content_type: str, external_id: str) -> ContentDetail:
    endpoint = "movie" if content_type == "movie" else "tv"
    append = "credits,videos,watch/providers,recommendations,keywords"
    raw = request_json(
        "GET",
        f"{BASE_URL}/{endpoint}/{external_id}",
        params=_params(append_to_response=append, region=settings.TMDB_REGION),
        service="TMDB",
    )
    if not raw.get("overview"):
        en_raw = request_json(
            "GET",
            f"{BASE_URL}/{endpoint}/{external_id}",
            params={**_params(), "language": "en-US"},
            service="TMDB",
        )
        raw["overview"] = en_raw.get("overview")
        raw["tagline"] = en_raw.get("tagline")
    return to_detail(raw, content_type)


def similar(content_type: str, external_id: str) -> list[ContentSummary]:
    endpoint = "movie" if content_type == "movie" else "tv"
    data = request_json(
        "GET", f"{BASE_URL}/{endpoint}/{external_id}/similar", params=_params(), service="TMDB"
    )
    return [to_summary(r, content_type) for r in data.get("results", [])]
