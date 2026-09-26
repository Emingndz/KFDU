from fastapi import APIRouter, Query, UploadFile, status

from app.core.deps import DbSession
from app.core.pagination import Page
from app.modules.users import service
from app.modules.users.avatars import delete_avatar_file, save_avatar
from app.modules.users.deps import CurrentUser, OptionalUser
from app.modules.users.schemas import (
    DeleteAccountIn,
    EmailChangeIn,
    MeOut,
    MeUpdateIn,
    ProfileOut,
    PublicUserOut,
    PublicUserWithFollowOut,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MeOut, summary="Kendi profilim")
def get_me(user: CurrentUser) -> MeOut:
    return MeOut.model_validate(user)


@router.patch("/me", response_model=MeOut, summary="Profilimi güncelle")
def update_me(payload: MeUpdateIn, user: CurrentUser, db: DbSession) -> MeOut:
    updated = service.update_me(db, user=user, payload=payload)
    return MeOut.model_validate(updated)


@router.put("/me/email", response_model=MeOut, summary="E-postamı değiştir")
def change_email(payload: EmailChangeIn, user: CurrentUser, db: DbSession) -> MeOut:
    updated = service.change_email(
        db, user=user, new_email=payload.new_email, current_password=payload.current_password
    )
    return MeOut.model_validate(updated)


@router.post("/me/avatar", summary="Avatar yükle")
async def upload_avatar(user: CurrentUser, db: DbSession, file: UploadFile) -> dict:
    data = await file.read()
    avatar_url = save_avatar(user.id, file.content_type or "", data)
    if user.avatar_url:
        delete_avatar_file(user.avatar_url)
    user.avatar_url = avatar_url
    db.commit()
    return {"avatar_url": avatar_url}


@router.delete("/me/avatar", summary="Avatarı kaldır")
def remove_avatar(user: CurrentUser, db: DbSession) -> dict:
    if user.avatar_url:
        delete_avatar_file(user.avatar_url)
        user.avatar_url = None
        db.commit()
    return {"avatar_url": None}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Hesabımı sil")
def delete_me(payload: DeleteAccountIn, user: CurrentUser, db: DbSession) -> None:
    service.delete_account(db, user=user, password=payload.password)


@router.get("/search", response_model=Page[PublicUserOut], summary="Kullanıcı ara")
def search_users(
    user: CurrentUser,
    db: DbSession,
    q: str = Query(min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[PublicUserOut]:
    return service.search_users(db, query=q, page=page, page_size=page_size)


@router.get("/suggestions", response_model=list[PublicUserOut], summary="Takip önerileri")
def get_suggestions(
    user: CurrentUser, db: DbSession, limit: int = Query(10, ge=1, le=50)
) -> list[PublicUserOut]:
    return service.suggestions(db, user=user, limit=limit)


@router.get("/{username}", response_model=ProfileOut, summary="Kullanıcı profili")
def get_profile(username: str, viewer: OptionalUser, db: DbSession) -> ProfileOut:
    return service.get_profile(db, viewer=viewer, username=username)


@router.post("/{username}/follow", summary="Kullanıcıyı takip et")
def follow_user(username: str, user: CurrentUser, db: DbSession) -> dict:
    following, followers_count = service.follow(db, follower=user, username=username)
    return {"following": following, "followers_count": followers_count}


@router.delete("/{username}/follow", summary="Takibi bırak")
def unfollow_user(username: str, user: CurrentUser, db: DbSession) -> dict:
    following, followers_count = service.unfollow(db, follower=user, username=username)
    return {"following": following, "followers_count": followers_count}


@router.get("/{username}/followers", response_model=Page[PublicUserWithFollowOut], summary="Takipçiler")
def get_followers(
    username: str,
    viewer: OptionalUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[PublicUserWithFollowOut]:
    return service.list_followers(db, viewer=viewer, username=username, page=page, page_size=page_size)


@router.get("/{username}/following", response_model=Page[PublicUserWithFollowOut], summary="Takip edilenler")
def get_following(
    username: str,
    viewer: OptionalUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[PublicUserWithFollowOut]:
    return service.list_following(db, viewer=viewer, username=username, page=page, page_size=page_size)
