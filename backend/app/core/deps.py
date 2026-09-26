from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

DbSession = Annotated[Session, Depends(get_db)]


class PageParams:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
