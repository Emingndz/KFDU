from datetime import UTC, date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core import events
from app.core.errors import conflict, forbidden, not_found
from app.core.pagination import Page
from app.modules.catalog import service as catalog_service
from app.modules.catalog.models import Content
from app.modules.library.models import LibraryEntry, Review
from app.modules.library.schemas import (
    ContentState,
    EntryOut,
    EntryUpdateIn,
    FriendEntry,
    LibraryStatus,
    LookupEntryOut,
    MeState,
    PlatformStats,
    ReviewBasicOut,
    ReviewCreateIn,
    ReviewUpdateIn,
)
from app.modules.users.models import Follow, User
from app.modules.users.schemas import PublicUserOut


def _entry_to_out(entry: LibraryEntry, content: Content) -> EntryOut:
    return EntryOut(
        content=catalog_service.content_to_summary(content),
        status=entry.status,
        rating=entry.rating,
        is_favorite=entry.is_favorite,
        progress=entry.progress,
        started_at=entry.started_at,
        finished_at=entry.finished_at,
        updated_at=entry.updated_at,
    )


def _empty_entry_out(content: Content) -> EntryOut:
    return EntryOut(
        content=catalog_service.content_to_summary(content),
        status=None,
        rating=None,
        is_favorite=False,
        progress=None,
        started_at=None,
        finished_at=None,
        updated_at=datetime.now(UTC),
    )


def _has_review(db: Session, *, user_id: int, content_id: int) -> bool:
    return (
        db.scalar(select(Review.id).where(Review.user_id == user_id, Review.content_id == content_id))
        is not None
    )


def upsert_entry(
    db: Session, *, user: User, content_type: str, external_id: str, data: EntryUpdateIn, silent: bool = False
) -> EntryOut:
    content = catalog_service.get_or_create_content(db, content_type, external_id)
    fields = data.model_fields_set

    entry = db.scalar(
        select(LibraryEntry).where(LibraryEntry.user_id == user.id, LibraryEntry.content_id == content.id)
    )
    is_new = entry is None
    old_rating = entry.rating if entry is not None else None
    old_status = entry.status if entry is not None else None
    if entry is None:
        entry = LibraryEntry(user_id=user.id, content_id=content.id)

    if "status" in fields:
        entry.status = data.status.value if data.status is not None else None
    if "rating" in fields:
        entry.rating = data.rating
        entry.rated_at = datetime.now(UTC) if data.rating is not None else None
    if "is_favorite" in fields and data.is_favorite is not None:
        entry.is_favorite = data.is_favorite
    if "progress" in fields:
        entry.progress = data.progress

    today = date.today()
    if entry.status == LibraryStatus.IN_PROGRESS.value and entry.started_at is None:
        entry.started_at = today
    if entry.status == LibraryStatus.COMPLETED.value and entry.finished_at is None:
        entry.finished_at = today

    status_changed = "status" in fields and entry.status != old_status
    rating_set = "rating" in fields and entry.rating is not None and entry.rating != old_rating
    rating_removed = "rating" in fields and entry.rating is None and old_rating is not None
    is_empty = not entry.status and entry.rating is None and entry.progress is None and not entry.is_favorite

    if rating_removed and not _has_review(db, user_id=user.id, content_id=content.id):
        events.emit("library.log_removed", db=db, user_id=user.id, content_id=content.id)

    if is_empty:
        if not is_new:
            db.delete(entry)
        db.commit()
        return _empty_entry_out(content)

    if is_new:
        db.add(entry)
    if rating_set:
        events.emit("library.log_changed", db=db, user_id=user.id, content_id=content.id, silent=silent)
    if status_changed:
        events.emit(
            "library.status_changed",
            db=db,
            user_id=user.id,
            content_id=content.id,
            status=entry.status,
            silent=silent,
        )

    db.commit()
    db.refresh(entry)
    return _entry_to_out(entry, content)


def delete_entry(db: Session, *, user: User, content_type: str, external_id: str) -> None:
    content = catalog_service.get_or_create_content(db, content_type, external_id)
    entry = db.scalar(
        select(LibraryEntry).where(LibraryEntry.user_id == user.id, LibraryEntry.content_id == content.id)
    )
    if entry is None:
        return

    had_rating = entry.rating is not None
    db.delete(entry)
    if had_rating and not _has_review(db, user_id=user.id, content_id=content.id):
        events.emit("library.log_removed", db=db, user_id=user.id, content_id=content.id)
    db.commit()


def get_state(db: Session, *, viewer: User | None, content_type: str, external_id: str) -> ContentState:
    content = catalog_service.get_or_create_content(db, content_type, external_id)

    average, count = db.execute(
        select(func.avg(LibraryEntry.rating), func.count(LibraryEntry.rating)).where(
            LibraryEntry.content_id == content.id, LibraryEntry.rating.is_not(None)
        )
    ).one()
    distribution_rows = db.execute(
        select(LibraryEntry.rating, func.count())
        .where(LibraryEntry.content_id == content.id, LibraryEntry.rating.is_not(None))
        .group_by(LibraryEntry.rating)
    ).all()
    distribution = {int(rating): int(cnt) for rating, cnt in distribution_rows}

    me = None
    friends: list[FriendEntry] = []
    if viewer is not None:
        my_entry = db.scalar(
            select(LibraryEntry).where(
                LibraryEntry.user_id == viewer.id, LibraryEntry.content_id == content.id
            )
        )
        my_review_id = db.scalar(
            select(Review.id).where(Review.user_id == viewer.id, Review.content_id == content.id)
        )
        entry_out = _entry_to_out(my_entry, content) if my_entry is not None else None
        me = MeState(entry=entry_out, review_id=my_review_id)

        followed_ids = select(Follow.followed_id).where(Follow.follower_id == viewer.id)
        rows = db.execute(
            select(User, LibraryEntry.rating, LibraryEntry.status)
            .join(LibraryEntry, LibraryEntry.user_id == User.id)
            .where(LibraryEntry.content_id == content.id, User.id.in_(followed_ids))
        ).all()
        friends = [
            FriendEntry(user=PublicUserOut.model_validate(u), rating=rating, status=entry_status)
            for u, rating, entry_status in rows
        ]

    platform = PlatformStats(
        average=round(average, 2) if average is not None else None,
        count=count or 0,
        distribution=distribution,
    )
    return ContentState(content_id=content.id, platform=platform, me=me, friends=friends)


def lookup(db: Session, *, user: User, keys: list[str]) -> dict[str, LookupEntryOut]:
    parsed = [(key, *key.split(":", 1)) for key in keys if ":" in key]
    if not parsed:
        return {}

    conditions = [
        (Content.type == content_type) & (Content.external_id == external_id)
        for _, content_type, external_id in parsed
    ]
    entry_cols = (LibraryEntry.status, LibraryEntry.rating, LibraryEntry.is_favorite)
    join_condition = (LibraryEntry.content_id == Content.id) & (LibraryEntry.user_id == user.id)
    rows = db.execute(
        select(Content.type, Content.external_id, *entry_cols)
        .join(LibraryEntry, join_condition)
        .where(or_(*conditions))
    ).all()
    found = {(t, e): (s, r, f) for t, e, s, r, f in rows}

    result: dict[str, LookupEntryOut] = {}
    for key, content_type, external_id in parsed:
        match = found.get((content_type, external_id))
        if match:
            status_value, rating, is_favorite = match
            result[key] = LookupEntryOut(status=status_value, rating=rating, is_favorite=is_favorite)
        else:
            result[key] = LookupEntryOut(status=None, rating=None, is_favorite=False)
    return result


def list_user_library(
    db: Session,
    *,
    username: str,
    content_type: str | None = None,
    status: str | None = None,
    favorite: bool | None = None,
    sort: str = "recent",
    page: int = 1,
    page_size: int = 20,
) -> Page[EntryOut]:
    target = db.scalar(select(User).where(User.username == username.lower()))
    if target is None:
        raise not_found("Kullanıcı bulunamadı")

    base = (
        select(LibraryEntry, Content)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(LibraryEntry.user_id == target.id)
    )
    if content_type:
        base = base.where(Content.type == content_type)
    if status:
        base = base.where(LibraryEntry.status == status)
    if favorite is not None:
        base = base.where(LibraryEntry.is_favorite == favorite)

    sort_map = {
        "recent": LibraryEntry.updated_at.desc(),
        "rating": LibraryEntry.rating.desc(),
        "title": Content.title.asc(),
        "year": Content.year.desc(),
    }
    base = base.order_by(sort_map.get(sort, LibraryEntry.updated_at.desc()))

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(base.offset((page - 1) * page_size).limit(page_size)).all()
    items = [_entry_to_out(entry, content) for entry, content in rows]
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


def create_review(db: Session, *, user: User, payload: ReviewCreateIn) -> ReviewBasicOut:
    content = catalog_service.get_or_create_content(db, payload.type.value, payload.external_id)
    if _has_review(db, user_id=user.id, content_id=content.id):
        raise conflict("REVIEW_EXISTS", "Bu içerik için zaten bir incelemen var")

    review = Review(
        user_id=user.id, content_id=content.id, body=payload.body, has_spoiler=payload.has_spoiler
    )
    db.add(review)
    events.emit("library.log_changed", db=db, user_id=user.id, content_id=content.id, silent=False)
    db.commit()
    db.refresh(review)
    return ReviewBasicOut(
        id=review.id,
        body=review.body,
        has_spoiler=review.has_spoiler,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def _get_owned_review(db: Session, *, user: User, review_id: int) -> Review:
    review = db.get(Review, review_id)
    if review is None:
        raise not_found("İnceleme bulunamadı")
    if review.user_id != user.id:
        raise forbidden("Bu incelemeyi düzenleyemezsin")
    return review


def update_review(db: Session, *, user: User, review_id: int, payload: ReviewUpdateIn) -> ReviewBasicOut:
    review = _get_owned_review(db, user=user, review_id=review_id)
    fields = payload.model_fields_set
    if "body" in fields and payload.body is not None:
        review.body = payload.body
    if "has_spoiler" in fields and payload.has_spoiler is not None:
        review.has_spoiler = payload.has_spoiler

    events.emit("library.log_changed", db=db, user_id=user.id, content_id=review.content_id, silent=False)
    db.commit()
    db.refresh(review)
    return ReviewBasicOut(
        id=review.id,
        body=review.body,
        has_spoiler=review.has_spoiler,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def delete_review(db: Session, *, user: User, review_id: int) -> None:
    review = _get_owned_review(db, user=user, review_id=review_id)
    content_id = review.content_id
    db.delete(review)
    db.flush()

    if not _has_review(db, user_id=user.id, content_id=content_id):
        has_rating = (
            db.scalar(
                select(LibraryEntry.rating).where(
                    LibraryEntry.user_id == user.id, LibraryEntry.content_id == content_id
                )
            )
            is not None
        )
        if not has_rating:
            events.emit("library.log_removed", db=db, user_id=user.id, content_id=content_id)
    db.commit()
