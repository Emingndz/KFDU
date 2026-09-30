from fastapi import APIRouter, Query

from app.core.deps import DbSession
from app.core.pagination import Page
from app.modules.catalog.schemas import ContentSummary, ContentType
from app.modules.stats import badges as badges_service
from app.modules.stats import service
from app.modules.stats.schemas import (
    BadgeOut,
    GoalOut,
    GoalUpdateIn,
    ProfileSummaryOut,
    UserStatsOut,
    WrappedOut,
)
from app.modules.users.deps import CurrentUser

router = APIRouter(tags=["stats"])


@router.get("/users/{username}/summary", response_model=ProfileSummaryOut, summary="Profil özeti")
def get_profile_summary(username: str, db: DbSession) -> ProfileSummaryOut:
    return service.get_profile_summary(db, username=username)


@router.get("/users/{username}/stats", response_model=UserStatsOut, summary="Kullanıcı istatistikleri")
def get_user_stats(username: str, db: DbSession, year: int | None = None) -> UserStatsOut:
    return service.get_user_stats(db, username=username, year=year)


@router.get("/users/me/wrapped", response_model=WrappedOut, summary="Yıllık özet")
def get_wrapped(user: CurrentUser, db: DbSession, year: int | None = None) -> WrappedOut:
    return service.get_wrapped(db, user=user, year=year)


@router.get("/users/me/goals", response_model=list[GoalOut], summary="Yıllık hedeflerim")
def get_goals(user: CurrentUser, db: DbSession, year: int | None = None) -> list[GoalOut]:
    return service.get_goals(db, user=user, year=year)


@router.put("/users/me/goals", response_model=list[GoalOut], summary="Yıllık hedeflerimi güncelle")
def set_goals(
    payload: list[GoalUpdateIn], user: CurrentUser, db: DbSession, year: int | None = None
) -> list[GoalOut]:
    return service.set_goals(db, user=user, year=year, goals=payload)


@router.get("/users/{username}/badges", response_model=list[BadgeOut], summary="Rozetler")
def get_badges(username: str, db: DbSession) -> list[BadgeOut]:
    return badges_service.get_badges(db, username=username)


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
