from fastapi import APIRouter, Query, status

from app.core.deps import DbSession
from app.core.pagination import CursorPage, Page
from app.modules.catalog.schemas import ContentType
from app.modules.social import service
from app.modules.social.schemas import (
    ActivityOut,
    CommentCreateIn,
    CommentOut,
    CommentUpdateIn,
    NotificationOut,
    ReviewDetail,
    ReviewOut,
)
from app.modules.users.deps import CurrentUser, OptionalUser
from app.modules.users.schemas import PublicUserOut

router = APIRouter(tags=["social"])


@router.get("/feed", response_model=CursorPage[ActivityOut], summary="Akış")
def get_feed(
    viewer: OptionalUser,
    db: DbSession,
    scope: str = "following",
    cursor: str | None = None,
    limit: int = Query(15, ge=1, le=50),
) -> CursorPage[ActivityOut]:
    return service.get_feed(db, viewer=viewer, scope=scope, cursor=cursor, limit=limit)


@router.get(
    "/users/{username}/activities",
    response_model=CursorPage[ActivityOut],
    summary="Kullanıcının aktiviteleri",
)
def get_user_activities(
    username: str,
    viewer: OptionalUser,
    db: DbSession,
    cursor: str | None = None,
    limit: int = Query(15, ge=1, le=50),
) -> CursorPage[ActivityOut]:
    return service.list_user_activities(db, username=username, viewer=viewer, cursor=cursor, limit=limit)


@router.get("/activities/{activity_id}", response_model=ActivityOut, summary="Aktivite detayı")
def get_activity(activity_id: int, viewer: OptionalUser, db: DbSession) -> ActivityOut:
    return service.get_activity(db, activity_id=activity_id, viewer=viewer)


@router.post("/activities/{activity_id}/like", summary="Aktiviteyi beğen")
def like_activity(activity_id: int, user: CurrentUser, db: DbSession) -> dict:
    liked, likes_count = service.like_activity(db, user=user, activity_id=activity_id)
    return {"liked": liked, "likes_count": likes_count}


@router.delete("/activities/{activity_id}/like", summary="Beğeniyi geri al")
def unlike_activity(activity_id: int, user: CurrentUser, db: DbSession) -> dict:
    liked, likes_count = service.unlike_activity(db, user=user, activity_id=activity_id)
    return {"liked": liked, "likes_count": likes_count}


@router.get("/activities/{activity_id}/likes", response_model=Page[PublicUserOut], summary="Beğenenler")
def list_activity_likes(activity_id: int, db: DbSession, page: int = Query(1, ge=1)) -> Page[PublicUserOut]:
    return service.list_activity_likes(db, activity_id=activity_id, page=page)


@router.get("/activities/{activity_id}/comments", response_model=CursorPage[CommentOut], summary="Yorumlar")
def list_comments(
    activity_id: int,
    viewer: OptionalUser,
    db: DbSession,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
) -> CursorPage[CommentOut]:
    return service.list_comments(db, viewer=viewer, activity_id=activity_id, cursor=cursor, limit=limit)


@router.post(
    "/activities/{activity_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Yorum ekle",
)
def add_comment(activity_id: int, payload: CommentCreateIn, user: CurrentUser, db: DbSession) -> CommentOut:
    return service.add_comment(db, user=user, activity_id=activity_id, body=payload.body)


@router.patch("/comments/{comment_id}", response_model=CommentOut, summary="Yorumu düzenle")
def update_comment(comment_id: int, payload: CommentUpdateIn, user: CurrentUser, db: DbSession) -> CommentOut:
    return service.update_comment(db, user=user, comment_id=comment_id, body=payload.body)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Yorumu sil")
def delete_comment(comment_id: int, user: CurrentUser, db: DbSession) -> None:
    service.delete_comment(db, user=user, comment_id=comment_id)


@router.get("/notifications", response_model=CursorPage[NotificationOut], summary="Bildirimler")
def list_notifications(
    user: CurrentUser, db: DbSession, cursor: str | None = None, limit: int = Query(20, ge=1, le=100)
) -> CursorPage[NotificationOut]:
    return service.list_notifications(db, user=user, cursor=cursor, limit=limit)


@router.get("/notifications/unread-count", summary="Okunmamış bildirim sayısı")
def get_unread_notifications_count(user: CurrentUser, db: DbSession) -> dict:
    return {"count": service.unread_notifications_count(db, user=user)}


@router.post(
    "/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT, summary="Tümünü okundu işaretle"
)
def mark_all_notifications_read(user: CurrentUser, db: DbSession) -> None:
    service.mark_all_notifications_read(db, user=user)


@router.post(
    "/notifications/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Bildirimi okundu işaretle",
)
def mark_notification_read(notification_id: int, user: CurrentUser, db: DbSession) -> None:
    service.mark_notification_read(db, user=user, notification_id=notification_id)


@router.get("/reviews", response_model=Page[ReviewOut], summary="İçeriğin incelemeleri")
def list_content_reviews(
    viewer: OptionalUser,
    db: DbSession,
    type: ContentType,
    external_id: str,
    sort: str = "new",
    page: int = Query(1, ge=1),
) -> Page[ReviewOut]:
    return service.list_content_reviews(
        db, content_type=type.value, external_id=external_id, sort=sort, page=page, viewer=viewer
    )


@router.get("/reviews/{review_id}", response_model=ReviewDetail, summary="İnceleme detayı")
def get_review_detail(review_id: int, viewer: OptionalUser, db: DbSession) -> ReviewDetail:
    return service.get_review_detail(db, review_id=review_id, viewer=viewer)


@router.get("/users/{username}/reviews", response_model=Page[ReviewOut], summary="Kullanıcının incelemeleri")
def get_user_reviews(
    username: str, viewer: OptionalUser, db: DbSession, page: int = Query(1, ge=1)
) -> Page[ReviewOut]:
    return service.list_user_reviews(db, username=username, page=page, viewer=viewer)
