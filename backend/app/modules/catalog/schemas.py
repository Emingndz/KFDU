from enum import StrEnum

from pydantic import BaseModel, Field


class ContentType(StrEnum):
    MOVIE = "movie"
    TV = "tv"
    BOOK = "book"


class ContentSource(StrEnum):
    TMDB = "tmdb"
    OPENLIBRARY = "openlibrary"
    GOOGLE_BOOKS = "google_books"


class Person(BaseModel):
    id: str | None = None
    name: str
    role: str | None = None
    photo_url: str | None = None


class Providers(BaseModel):
    flatrate: list[str] = Field(default_factory=list)
    rent: list[str] = Field(default_factory=list)
    buy: list[str] = Field(default_factory=list)
    link: str | None = None


class GenreOut(BaseModel):
    key: str
    label: str


class SeasonOut(BaseModel):
    number: int
    name: str
    episode_count: int
    air_year: int | None = None
    poster_url: str | None = None


class ContentSummary(BaseModel):
    id: int | None = None
    type: ContentType
    source: ContentSource
    external_id: str
    title: str
    original_title: str | None = None
    year: int | None = None
    poster_url: str | None = None
    genres: list[str] = Field(default_factory=list)
    external_rating: float | None = None
    creators: list[str] = Field(default_factory=list)


class ContentDetail(ContentSummary):
    backdrop_url: str | None = None
    overview: str | None = None
    runtime_minutes: int | None = None
    page_count: int | None = None
    seasons: int | None = None
    seasons_detail: list[SeasonOut] = Field(default_factory=list)
    original_language: str | None = None
    genres_detail: list[GenreOut] = Field(default_factory=list)
    directors: list[Person] = Field(default_factory=list)
    authors: list[Person] = Field(default_factory=list)
    cast: list[Person] = Field(default_factory=list)
    trailer_key: str | None = None
    providers: Providers = Field(default_factory=Providers)
    external_votes: int | None = None
    isbn: list[str] = Field(default_factory=list)
    external_url: str | None = None
    novel_authors: list[str] = Field(default_factory=list)
    has_book_keyword: bool = False


class PersonCredit(BaseModel):
    type: ContentType
    external_id: str
    title: str
    poster_url: str | None = None
    year: int | None = None


class PersonDetail(BaseModel):
    id: str
    name: str
    photo_url: str | None = None
    biography: str | None = None
    birthday: str | None = None
    birth_place: str | None = None
    known_for: str | None = None
    directing: list[PersonCredit] = Field(default_factory=list)
    acting: list[PersonCredit] = Field(default_factory=list)


class AuthorWork(BaseModel):
    external_id: str
    title: str
    poster_url: str | None = None
    year: int | None = None


class AuthorDetail(BaseModel):
    id: str
    name: str
    photo_url: str | None = None
    biography: str | None = None
    birth_date: str | None = None
    death_date: str | None = None
    works: list[AuthorWork] = Field(default_factory=list)


class DiscoverParams(BaseModel):
    type: ContentType
    genre: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    min_rating: float | None = None
    sort: str = "popular"
    language: str | None = None
    page: int = 1
