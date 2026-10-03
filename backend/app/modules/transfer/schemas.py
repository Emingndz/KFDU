from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ExportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"


class ImportSource(StrEnum):
    LETTERBOXD = "letterboxd"
    GOODREADS = "goodreads"


class ImportStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class ImportFileKind(StrEnum):
    RATINGS = "ratings"
    DIARY = "diary"
    REVIEWS = "reviews"
    ARCHIVE = "archive"
    WATCHED = "watched"
    WATCHLIST = "watchlist"
    GOODREADS_LIBRARY = "goodreads_library"


class ImportStartOut(BaseModel):
    job_id: int


class ImportReport(BaseModel):
    file_kind: ImportFileKind | None
    unmatched: list[str]


class ImportJobOut(BaseModel):
    id: int
    source: ImportSource
    status: ImportStatus
    total: int
    processed: int
    matched: int
    report: ImportReport
    error: str | None
    created_at: datetime
    finished_at: datetime | None
