from pydantic import BaseModel


class ProfileSummaryOut(BaseModel):
    movies_completed: int
    tv_completed: int
    books_completed: int
    ratings: int
    reviews: int
    lists: int
    favorites: int
