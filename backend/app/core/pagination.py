from pydantic import BaseModel


class Page[T](BaseModel):
    items: list[T]
    page: int
    page_size: int
    total: int | None
    has_next: bool


class CursorPage[T](BaseModel):
    items: list[T]
    next_cursor: str | None
