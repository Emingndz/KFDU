from pydantic import BaseModel, Field

from app.modules.catalog.schemas import ContentSummary


class ProfileSummaryOut(BaseModel):
    movies_completed: int
    tv_completed: int
    books_completed: int
    ratings: int
    reviews: int
    lists: int
    favorites: int


class StatsTotals(BaseModel):
    movies: int
    tv: int
    books: int
    minutes: int
    pages: int
    reviews: int
    avg_rating: float | None = None


class GenreCount(BaseModel):
    key: str
    label: str
    count: int


class MonthlyCount(BaseModel):
    month: int
    movies: int
    tv: int
    books: int


class PersonCount(BaseModel):
    name: str
    count: int


class StatsHighlights(BaseModel):
    longest_movie: ContentSummary | None = None
    longest_book: ContentSummary | None = None
    highest_rated: list[ContentSummary] = Field(default_factory=list)


class UserStatsOut(BaseModel):
    year: int
    totals: StatsTotals
    rating_distribution: dict[int, int] = Field(default_factory=dict)
    top_genres: list[GenreCount] = Field(default_factory=list)
    monthly: list[MonthlyCount] = Field(default_factory=list)
    top_people: list[PersonCount] = Field(default_factory=list)
    highlights: StatsHighlights = Field(default_factory=StatsHighlights)


class WrappedReview(BaseModel):
    id: int
    content: ContentSummary
    excerpt: str
    likes_count: int


class WrappedOut(BaseModel):
    stats: UserStatsOut
    first_completed: ContentSummary | None = None
    last_completed: ContentSummary | None = None
    most_liked_review: WrappedReview | None = None
    most_active_month: int | None = None
    dominant_genre: GenreCount | None = None
    fun_title: str | None = None
