from fastapi import APIRouter, Query

from app.core.deps import DbSession
from app.core.pagination import Page
from app.modules.catalog.schemas import ContentSummary, ContentType
from app.modules.stats import service
from app.modules.stats.schemas import ProfileSummaryOut

router = APIRouter(tags=["stats"])


@router.get("/users/{username}/summary", response_model=ProfileSummaryOut, summary="Profil özeti")
def get_profile_summary(username: str, db: DbSession) -> ProfileSummaryOut:
    return service.get_profile_summary(db, username=username)


@router.get("/platform/top-rated", response_model=Page[ContentSummary], summary="En yüksek puanlılar")
def get_top_rated(
    db: DbSession,
    type: ContentType | None = None,
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
) -> Page[ContentSummary]:
    return service.get_top_rated(db, content_type=type.value if type else None, page=page, page_size=limit)


@router.get("/platform/popular", response_model=list[ContentSummary], summary="En popülerler")
def get_popular(
    db: DbSession,
    type: ContentType | None = None,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
) -> list[ContentSummary]:
    return service.get_popular(db, content_type=type.value if type else None, days=days, limit=limit)
