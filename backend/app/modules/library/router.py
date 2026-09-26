from fastapi import APIRouter, status

from app.core.deps import DbSession
from app.core.pagination import Page
from app.modules.library import service
from app.modules.library.schemas import (
    ContentState,
    EntryOut,
    EntryUpdateIn,
    LookupEntryOut,
    LookupIn,
    ReviewBasicOut,
    ReviewCreateIn,
    ReviewUpdateIn,
)
from app.modules.users.deps import CurrentUser, OptionalUser

router = APIRouter(tags=["library"])


@router.put("/library/{type}/{external_id}", response_model=EntryOut, summary="Kütüphane girişini güncelle")
def upsert_entry(
    type: str, external_id: str, payload: EntryUpdateIn, user: CurrentUser, db: DbSession
) -> EntryOut:
    return service.upsert_entry(db, user=user, content_type=type, external_id=external_id, data=payload)


@router.delete(
    "/library/{type}/{external_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kütüphane girişini sil",
)
def delete_entry(type: str, external_id: str, user: CurrentUser, db: DbSession) -> None:
    service.delete_entry(db, user=user, content_type=type, external_id=external_id)


@router.get("/library/{type}/{external_id}/state", response_model=ContentState, summary="İçerik durumu")
def get_state(type: str, external_id: str, viewer: OptionalUser, db: DbSession) -> ContentState:
    return service.get_state(db, viewer=viewer, content_type=type, external_id=external_id)


@router.post("/library/lookup", response_model=dict[str, LookupEntryOut], summary="Toplu kütüphane bakışı")
def lookup(payload: LookupIn, user: CurrentUser, db: DbSession) -> dict[str, LookupEntryOut]:
    return service.lookup(db, user=user, keys=payload.keys)


@router.get("/users/{username}/library", response_model=Page[EntryOut], summary="Kullanıcının kütüphanesi")
def get_user_library(
    username: str,
    viewer: OptionalUser,
    db: DbSession,
    type: str | None = None,
    status: str | None = None,
    favorite: bool | None = None,
    sort: str = "recent",
    page: int = 1,
    page_size: int = 20,
) -> Page[EntryOut]:
    return service.list_user_library(
        db,
        username=username,
        content_type=type,
        status=status,
        favorite=favorite,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/reviews", response_model=ReviewBasicOut, status_code=status.HTTP_201_CREATED, summary="İnceleme yaz"
)
def create_review(payload: ReviewCreateIn, user: CurrentUser, db: DbSession) -> ReviewBasicOut:
    return service.create_review(db, user=user, payload=payload)


@router.patch("/reviews/{review_id}", response_model=ReviewBasicOut, summary="İncelemeyi düzenle")
def update_review(
    review_id: int, payload: ReviewUpdateIn, user: CurrentUser, db: DbSession
) -> ReviewBasicOut:
    return service.update_review(db, user=user, review_id=review_id, payload=payload)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="İncelemeyi sil")
def delete_review(review_id: int, user: CurrentUser, db: DbSession) -> None:
    service.delete_review(db, user=user, review_id=review_id)
