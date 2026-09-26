from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core import events
from app.core.errors import bad_request, conflict, not_found
from app.core.pagination import Page
from app.core.security import verify_password
from app.modules.users.avatars import delete_avatar_file
from app.modules.users.models import Follow, User
from app.modules.users.schemas import MeUpdateIn, ProfileOut, PublicUserOut, PublicUserWithFollowOut


def _page(items: list, *, page: int, page_size: int, total: int) -> Page:
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


def get_profile(db: Session, *, viewer: User | None, username: str) -> ProfileOut:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        raise not_found("Kullanıcı bulunamadı")

    followers_count = (
        db.scalar(select(func.count()).select_from(Follow).where(Follow.followed_id == user.id)) or 0
    )
    following_count = (
        db.scalar(select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)) or 0
    )
    is_following = viewer is not None and db.get(Follow, (viewer.id, user.id)) is not None
    follows_me = viewer is not None and db.get(Follow, (user.id, viewer.id)) is not None

    return ProfileOut(
        **PublicUserOut.model_validate(user).model_dump(),
        created_at=user.created_at,
        followers_count=followers_count,
        following_count=following_count,
        is_following=is_following,
        follows_me=follows_me,
        is_me=viewer is not None and viewer.id == user.id,
    )


def update_me(db: Session, *, user: User, payload: MeUpdateIn) -> User:
    data = payload.model_dump(exclude_unset=True)
    if "username" in data and data["username"] != user.username:
        if db.scalar(select(User).where(User.username == data["username"])) is not None:
            raise conflict("USERNAME_TAKEN", "Bu kullanıcı adı alınmış")
        user.username = data["username"]
    if "display_name" in data:
        user.display_name = data["display_name"]
    if "bio" in data:
        user.bio = data["bio"]
    if "favorite_genres" in data:
        user.favorite_genres = data["favorite_genres"] or []
    db.commit()
    db.refresh(user)
    return user


def change_email(db: Session, *, user: User, new_email: str, current_password: str) -> User:
    valid, _ = verify_password(current_password, user.password_hash)
    if not valid:
        raise bad_request("INVALID_PASSWORD", "Şifren yanlış")
    if new_email != user.email and db.scalar(select(User).where(User.email == new_email)) is not None:
        raise conflict("EMAIL_TAKEN", "Bu e-posta zaten kullanımda")
    user.email = new_email
    db.commit()
    db.refresh(user)
    return user


def _get_target_user(db: Session, username: str) -> User:
    target = db.scalar(select(User).where(User.username == username.lower()))
    if target is None:
        raise not_found("Kullanıcı bulunamadı")
    return target


def follow(db: Session, *, follower: User, username: str) -> tuple[bool, int]:
    target = _get_target_user(db, username)
    if target.id == follower.id:
        raise bad_request("CANNOT_FOLLOW_SELF", "Kendini takip edemezsin")

    if db.get(Follow, (follower.id, target.id)) is None:
        db.add(Follow(follower_id=follower.id, followed_id=target.id))
        events.emit("users.followed", db=db, follower_id=follower.id, followed_id=target.id)
        db.commit()

    followers_count = (
        db.scalar(select(func.count()).select_from(Follow).where(Follow.followed_id == target.id)) or 0
    )
    return True, followers_count


def unfollow(db: Session, *, follower: User, username: str) -> tuple[bool, int]:
    target = _get_target_user(db, username)

    existing = db.get(Follow, (follower.id, target.id))
    if existing is not None:
        db.delete(existing)
        db.commit()

    followers_count = (
        db.scalar(select(func.count()).select_from(Follow).where(Follow.followed_id == target.id)) or 0
    )
    return False, followers_count


def _following_ids_of(db: Session, viewer: User | None, target_ids: list[int]) -> set[int]:
    if viewer is None or not target_ids:
        return set()
    rows = db.scalars(
        select(Follow.followed_id).where(Follow.follower_id == viewer.id, Follow.followed_id.in_(target_ids))
    )
    return set(rows)


def list_followers(
    db: Session, *, viewer: User | None, username: str, page: int, page_size: int
) -> Page[PublicUserWithFollowOut]:
    user = _get_target_user(db, username)
    base = select(User).join(Follow, Follow.follower_id == User.id).where(Follow.followed_id == user.id)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(
        base.order_by(Follow.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()

    following_ids = _following_ids_of(db, viewer, [r.id for r in rows])
    items = [
        PublicUserWithFollowOut(
            **PublicUserOut.model_validate(r).model_dump(), is_following=r.id in following_ids
        )
        for r in rows
    ]
    return _page(items, page=page, page_size=page_size, total=total)


def list_following(
    db: Session, *, viewer: User | None, username: str, page: int, page_size: int
) -> Page[PublicUserWithFollowOut]:
    user = _get_target_user(db, username)
    base = select(User).join(Follow, Follow.followed_id == User.id).where(Follow.follower_id == user.id)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(
        base.order_by(Follow.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()

    following_ids = _following_ids_of(db, viewer, [r.id for r in rows])
    items = [
        PublicUserWithFollowOut(
            **PublicUserOut.model_validate(r).model_dump(), is_following=r.id in following_ids
        )
        for r in rows
    ]
    return _page(items, page=page, page_size=page_size, total=total)


def search_users(db: Session, *, query: str, page: int, page_size: int) -> Page[PublicUserOut]:
    if len(query) < 2:
        raise bad_request("QUERY_TOO_SHORT", "Arama en az 2 karakter olmalı")

    pattern = f"%{query.lower()}%"
    base = select(User).where(
        or_(func.lower(User.username).like(pattern), func.lower(User.display_name).like(pattern))
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(base.order_by(User.username).offset((page - 1) * page_size).limit(page_size)).all()
    items = [PublicUserOut.model_validate(r) for r in rows]
    return _page(items, page=page, page_size=page_size, total=total)


def suggestions(db: Session, *, user: User, limit: int = 10) -> list[PublicUserOut]:
    followed_ids = select(Follow.followed_id).where(Follow.follower_id == user.id)
    followers_count = func.count(Follow.follower_id).label("followers_count")

    rows = db.execute(
        select(User, followers_count)
        .outerjoin(Follow, Follow.followed_id == User.id)
        .where(User.id != user.id, User.id.notin_(followed_ids))
        .group_by(User.id)
        .order_by(followers_count.desc())
        .limit(limit)
    ).all()
    return [PublicUserOut.model_validate(row[0]) for row in rows]


def delete_account(db: Session, *, user: User, password: str) -> None:
    valid, _ = verify_password(password, user.password_hash)
    if not valid:
        raise bad_request("INVALID_PASSWORD", "Şifren yanlış")
    if user.avatar_url:
        delete_avatar_file(user.avatar_url)
    db.delete(user)
    db.commit()
