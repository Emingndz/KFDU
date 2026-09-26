from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.core.pagination import Page
from app.modules.catalog import service as catalog_service
from app.modules.catalog.models import Content
from app.modules.catalog.schemas import ContentSummary
from app.modules.library.models import LibraryEntry, Review
from app.modules.lists.models import ListItem, UserList
from app.modules.stats.schemas import ProfileSummaryOut
from app.modules.users.models import User

BAYES_M = 3
DEFAULT_RATING_MID = 5.5


def _count(db: Session, model: type, **filters: object) -> int:
    conditions = [getattr(model, key) == value for key, value in filters.items()]
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


def get_profile_summary(db: Session, *, username: str) -> ProfileSummaryOut:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        raise not_found("Kullanıcı bulunamadı")

    def completed(content_type: str) -> int:
        return (
            db.scalar(
                select(func.count())
                .select_from(LibraryEntry)
                .join(Content, Content.id == LibraryEntry.content_id)
                .where(
                    LibraryEntry.user_id == user.id,
                    LibraryEntry.status == "completed",
                    Content.type == content_type,
                )
            )
            or 0
        )

    ratings = (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .where(LibraryEntry.user_id == user.id, LibraryEntry.rating.is_not(None))
        )
        or 0
    )
    favorites = (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .where(LibraryEntry.user_id == user.id, LibraryEntry.is_favorite.is_(True))
        )
        or 0
    )

    return ProfileSummaryOut(
        movies_completed=completed("movie"),
        tv_completed=completed("tv"),
        books_completed=completed("book"),
        ratings=ratings,
        reviews=_count(db, Review, user_id=user.id),
        lists=_count(db, UserList, user_id=user.id),
        favorites=favorites,
    )


def get_top_rated(
    db: Session, *, content_type: str | None, page: int, page_size: int = 20
) -> Page[ContentSummary]:
    base_filter = [LibraryEntry.rating.is_not(None)]
    if content_type:
        base_filter.append(Content.type == content_type)

    overall_avg = db.scalar(
        select(func.avg(LibraryEntry.rating))
        .select_from(LibraryEntry)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(*base_filter)
    )
    overall_c = overall_avg or DEFAULT_RATING_MID

    rows = db.execute(
        select(Content.id, func.avg(LibraryEntry.rating), func.count(LibraryEntry.rating))
        .select_from(LibraryEntry)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(*base_filter)
        .group_by(Content.id)
        .having(func.count(LibraryEntry.rating) >= 1)
    ).all()

    scored = []
    for content_id, avg_rating, vote_count in rows:
        weight = vote_count / (vote_count + BAYES_M)
        score = weight * avg_rating + (1 - weight) * overall_c
        scored.append((content_id, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    total = len(scored)
    page_ids = [content_id for content_id, _ in scored[(page - 1) * page_size : page * page_size]]
    contents = {c.id: c for c in db.scalars(select(Content).where(Content.id.in_(page_ids)))}
    items = [catalog_service.content_to_summary(contents[cid]) for cid in page_ids if cid in contents]

    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


def get_popular(db: Session, *, content_type: str | None, days: int, limit: int) -> list[ContentSummary]:
    def compute(since: datetime | None) -> list[tuple[int, int]]:
        entry_where = () if since is None else (LibraryEntry.created_at >= since,)
        review_where = () if since is None else (Review.created_at >= since,)
        item_where = () if since is None else (ListItem.added_at >= since,)

        entry_counts = db.execute(
            select(LibraryEntry.content_id, func.count())
            .where(*entry_where)
            .group_by(LibraryEntry.content_id)
        ).all()
        review_counts = db.execute(
            select(Review.content_id, func.count()).where(*review_where).group_by(Review.content_id)
        ).all()
        item_counts = db.execute(
            select(ListItem.content_id, func.count())
            .join(UserList, UserList.id == ListItem.list_id)
            .where(UserList.is_public.is_(True), *item_where)
            .group_by(ListItem.content_id)
        ).all()

        totals: dict[int, int] = defaultdict(int)
        for content_id, cnt in entry_counts:
            totals[content_id] += cnt
        for content_id, cnt in review_counts:
            totals[content_id] += cnt * 2
        for content_id, cnt in item_counts:
            totals[content_id] += cnt
        return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)

    since = datetime.now(UTC) - timedelta(days=days)
    scored = compute(since)
    if len(scored) < 5:
        scored = compute(None)

    if content_type:
        candidate_ids = [content_id for content_id, _ in scored]
        matching_ids = set(
            db.scalars(select(Content.id).where(Content.type == content_type, Content.id.in_(candidate_ids)))
        )
        scored = [(cid, s) for cid, s in scored if cid in matching_ids]

    top_ids = [content_id for content_id, _ in scored[:limit]]
    contents = {c.id: c for c in db.scalars(select(Content).where(Content.id.in_(top_ids)))}
    return [catalog_service.content_to_summary(contents[cid]) for cid in top_ids if cid in contents]
