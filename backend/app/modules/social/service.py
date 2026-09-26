from collections import defaultdict

from sqlalchemy import func, or_, select, tuple_, update
from sqlalchemy.orm import Session

from app.core.errors import forbidden, not_found
from app.core.pagination import CursorPage, Page
from app.modules.catalog import service as catalog_service
from app.modules.catalog.models import Content
from app.modules.library.models import LibraryEntry, Review
from app.modules.lists.models import ListItem, UserList
from app.modules.social.models import Activity, ActivityComment, ActivityLike, Notification
from app.modules.social.schemas import (
    ActivityOut,
    CommentOut,
    CommentPreview,
    ListPreview,
    NotificationOut,
    ReviewDetail,
    ReviewOut,
    ReviewPreview,
)
from app.modules.users.models import Follow, User
from app.modules.users.schemas import PublicUserOut


def _count(db: Session, model: type, **filters: object) -> int:
    conditions = [getattr(model, key) == value for key, value in filters.items()]
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


def _make_excerpt(body: str, limit: int = 200) -> tuple[str, bool]:
    if len(body) <= limit:
        return body, False
    truncated = body[:limit]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return f"{truncated}…", True


def _hydrate_activities(db: Session, activities: list[Activity], *, viewer: User | None) -> list[ActivityOut]:
    if not activities:
        return []

    activity_ids = [a.id for a in activities]
    actor_ids = {a.actor_id for a in activities}
    content_ids = {a.content_id for a in activities if a.content_id is not None}
    list_ids = {a.list_id for a in activities if a.list_id is not None}

    actors = {u.id: u for u in db.scalars(select(User).where(User.id.in_(actor_ids)))}
    contents = (
        {c.id: c for c in db.scalars(select(Content).where(Content.id.in_(content_ids)))}
        if content_ids
        else {}
    )

    lists_info: dict[int, ListPreview] = {}
    if list_ids:
        user_lists = {ul.id: ul for ul in db.scalars(select(UserList).where(UserList.id.in_(list_ids)))}
        item_rows = db.execute(
            select(ListItem.list_id, Content.poster_url)
            .join(Content, Content.id == ListItem.content_id)
            .where(ListItem.list_id.in_(list_ids))
            .order_by(ListItem.list_id, ListItem.position)
        ).all()
        covers_by_list: dict[int, list[str | None]] = defaultdict(list)
        for list_id, poster_url in item_rows:
            covers_by_list[list_id].append(poster_url)
        for list_id, user_list in user_lists.items():
            covers = covers_by_list.get(list_id, [])
            lists_info[list_id] = ListPreview(
                id=user_list.id,
                title=user_list.title,
                item_count=len(covers),
                cover_urls=[c for c in covers if c][:4],
            )

    likes_counts = dict(
        db.execute(
            select(ActivityLike.activity_id, func.count())
            .where(ActivityLike.activity_id.in_(activity_ids))
            .group_by(ActivityLike.activity_id)
        ).all()
    )
    liked_by_me: set[int] = set()
    if viewer is not None:
        liked_by_me = set(
            db.scalars(
                select(ActivityLike.activity_id).where(
                    ActivityLike.activity_id.in_(activity_ids), ActivityLike.user_id == viewer.id
                )
            )
        )

    comment_rows = db.execute(
        select(ActivityComment, User)
        .join(User, User.id == ActivityComment.user_id)
        .where(ActivityComment.activity_id.in_(activity_ids))
        .order_by(ActivityComment.activity_id, ActivityComment.created_at.desc())
    ).all()
    comments_by_activity: dict[int, list[tuple[ActivityComment, User]]] = defaultdict(list)
    for comment, author in comment_rows:
        comments_by_activity[comment.activity_id].append((comment, author))

    log_pairs = [(a.actor_id, a.content_id) for a in activities if a.verb == "log"]
    ratings_by_pair: dict[tuple[int, int], int | None] = {}
    review_by_pair: dict[tuple[int, int], Review] = {}
    if log_pairs:
        entry_rows = db.execute(
            select(LibraryEntry.user_id, LibraryEntry.content_id, LibraryEntry.rating).where(
                tuple_(LibraryEntry.user_id, LibraryEntry.content_id).in_(log_pairs)
            )
        ).all()
        ratings_by_pair = {(u, c): r for u, c, r in entry_rows}
        review_rows = db.scalars(
            select(Review).where(tuple_(Review.user_id, Review.content_id).in_(log_pairs))
        ).all()
        review_by_pair = {(r.user_id, r.content_id): r for r in review_rows}

    items = []
    for activity in activities:
        actor = PublicUserOut.model_validate(actors[activity.actor_id])
        content = (
            catalog_service.content_to_summary(contents[activity.content_id])
            if activity.content_id in contents
            else None
        )

        rating: int | None = None
        review_preview: ReviewPreview | None = None
        list_preview: ListPreview | None = None
        card_type = activity.verb

        if activity.verb == "log":
            pair = (activity.actor_id, activity.content_id)
            rating = ratings_by_pair.get(pair)
            review = review_by_pair.get(pair)
            if review is not None:
                card_type = "review"
                excerpt, is_truncated = _make_excerpt(review.body)
                review_preview = ReviewPreview(
                    id=review.id, excerpt=excerpt, is_truncated=is_truncated, has_spoiler=review.has_spoiler
                )
            else:
                card_type = "rating"
        elif activity.verb in ("list_add", "list_create") and activity.list_id in lists_info:
            list_preview = lists_info[activity.list_id]

        raw_comments = comments_by_activity.get(activity.id, [])
        comments_preview = [
            CommentPreview(id=c.id, author=PublicUserOut.model_validate(author), body=c.body)
            for c, author in raw_comments[:2]
        ]

        items.append(
            ActivityOut(
                id=activity.id,
                card_type=card_type,
                actor=actor,
                content=content,
                rating=rating,
                review=review_preview,
                status=activity.status,
                list=list_preview,
                created_at=activity.created_at,
                likes_count=likes_counts.get(activity.id, 0),
                liked_by_me=activity.id in liked_by_me,
                comments_count=len(raw_comments),
                comments_preview=comments_preview,
            )
        )
    return items


def get_feed(
    db: Session, *, viewer: User | None, scope: str, cursor: str | None, limit: int = 15
) -> CursorPage[ActivityOut]:
    query = select(Activity)
    if scope == "following" and viewer is not None:
        followed_ids = select(Follow.followed_id).where(Follow.follower_id == viewer.id)
        query = query.where(or_(Activity.actor_id.in_(followed_ids), Activity.actor_id == viewer.id))
    if cursor:
        query = query.where(Activity.id < int(cursor))
    query = query.order_by(Activity.id.desc()).limit(limit + 1)

    activities = list(db.scalars(query).all())
    has_more = len(activities) > limit
    activities = activities[:limit]
    next_cursor = str(activities[-1].id) if has_more and activities else None

    return CursorPage(items=_hydrate_activities(db, activities, viewer=viewer), next_cursor=next_cursor)


def list_user_activities(
    db: Session, *, username: str, viewer: User | None, cursor: str | None, limit: int = 15
) -> CursorPage[ActivityOut]:
    target = db.scalar(select(User).where(User.username == username.lower()))
    if target is None:
        raise not_found("Kullanıcı bulunamadı")

    query = select(Activity).where(Activity.actor_id == target.id)
    if cursor:
        query = query.where(Activity.id < int(cursor))
    query = query.order_by(Activity.id.desc()).limit(limit + 1)

    activities = list(db.scalars(query).all())
    has_more = len(activities) > limit
    activities = activities[:limit]
    next_cursor = str(activities[-1].id) if has_more and activities else None

    return CursorPage(items=_hydrate_activities(db, activities, viewer=viewer), next_cursor=next_cursor)


def get_activity(db: Session, *, activity_id: int, viewer: User | None) -> ActivityOut:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise not_found("Aktivite bulunamadı")
    return _hydrate_activities(db, [activity], viewer=viewer)[0]


def like_activity(db: Session, *, user: User, activity_id: int) -> tuple[bool, int]:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise not_found("Aktivite bulunamadı")

    existing = db.get(ActivityLike, (activity_id, user.id))
    if existing is None:
        db.add(ActivityLike(activity_id=activity_id, user_id=user.id))
        if activity.actor_id != user.id:
            duplicate = db.scalar(
                select(Notification).where(
                    Notification.recipient_id == activity.actor_id,
                    Notification.actor_id == user.id,
                    Notification.type == "like",
                    Notification.activity_id == activity_id,
                )
            )
            if duplicate is None:
                db.add(
                    Notification(
                        recipient_id=activity.actor_id,
                        actor_id=user.id,
                        type="like",
                        activity_id=activity_id,
                    )
                )
        db.commit()

    return True, _count(db, ActivityLike, activity_id=activity_id)


def unlike_activity(db: Session, *, user: User, activity_id: int) -> tuple[bool, int]:
    existing = db.get(ActivityLike, (activity_id, user.id))
    if existing is not None:
        db.delete(existing)
        db.commit()

    return False, _count(db, ActivityLike, activity_id=activity_id)


def list_activity_likes(
    db: Session, *, activity_id: int, page: int, page_size: int = 20
) -> Page[PublicUserOut]:
    base = (
        select(User)
        .join(ActivityLike, ActivityLike.user_id == User.id)
        .where(ActivityLike.activity_id == activity_id)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(base.offset((page - 1) * page_size).limit(page_size)).all()
    items = [PublicUserOut.model_validate(u) for u in rows]
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


def _comment_to_out(
    comment: ActivityComment, *, author: User, viewer: User | None, activity_owner_id: int
) -> CommentOut:
    can_edit = viewer is not None and viewer.id == comment.user_id
    can_delete = viewer is not None and (viewer.id == comment.user_id or viewer.id == activity_owner_id)
    return CommentOut(
        id=comment.id,
        activity_id=comment.activity_id,
        author=PublicUserOut.model_validate(author),
        body=comment.body,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        can_edit=can_edit,
        can_delete=can_delete,
    )


def list_comments(
    db: Session, *, viewer: User | None, activity_id: int, cursor: str | None, limit: int = 20
) -> CursorPage[CommentOut]:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise not_found("Aktivite bulunamadı")

    query = (
        select(ActivityComment, User)
        .join(User, User.id == ActivityComment.user_id)
        .where(ActivityComment.activity_id == activity_id)
    )
    if cursor:
        query = query.where(ActivityComment.id > int(cursor))
    query = query.order_by(ActivityComment.id.asc()).limit(limit + 1)

    rows = db.execute(query).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = str(rows[-1][0].id) if has_more and rows else None

    items = [
        _comment_to_out(comment, author=author, viewer=viewer, activity_owner_id=activity.actor_id)
        for comment, author in rows
    ]
    return CursorPage(items=items, next_cursor=next_cursor)


def add_comment(db: Session, *, user: User, activity_id: int, body: str) -> CommentOut:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise not_found("Aktivite bulunamadı")

    comment = ActivityComment(activity_id=activity_id, user_id=user.id, body=body)
    db.add(comment)
    db.flush()
    if activity.actor_id != user.id:
        db.add(
            Notification(
                recipient_id=activity.actor_id,
                actor_id=user.id,
                type="comment",
                activity_id=activity_id,
                comment_id=comment.id,
            )
        )
    db.commit()
    db.refresh(comment)
    return _comment_to_out(comment, author=user, viewer=user, activity_owner_id=activity.actor_id)


def update_comment(db: Session, *, user: User, comment_id: int, body: str) -> CommentOut:
    comment = db.get(ActivityComment, comment_id)
    if comment is None:
        raise not_found("Yorum bulunamadı")
    if comment.user_id != user.id:
        raise forbidden("Bu yorumu düzenleyemezsin")

    comment.body = body
    db.commit()
    db.refresh(comment)
    activity = db.get(Activity, comment.activity_id)
    return _comment_to_out(comment, author=user, viewer=user, activity_owner_id=activity.actor_id)


def delete_comment(db: Session, *, user: User, comment_id: int) -> None:
    comment = db.get(ActivityComment, comment_id)
    if comment is None:
        raise not_found("Yorum bulunamadı")
    activity = db.get(Activity, comment.activity_id)
    if comment.user_id != user.id and activity.actor_id != user.id:
        raise forbidden("Bu yorumu silemezsin")
    db.delete(comment)
    db.commit()


def list_notifications(
    db: Session, *, user: User, cursor: str | None, limit: int = 20
) -> CursorPage[NotificationOut]:
    query = select(Notification).where(Notification.recipient_id == user.id)
    if cursor:
        query = query.where(Notification.id < int(cursor))
    query = query.order_by(Notification.id.desc()).limit(limit + 1)

    rows = list(db.scalars(query).all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = str(rows[-1].id) if has_more and rows else None

    actor_ids = {n.actor_id for n in rows}
    actors = {u.id: u for u in db.scalars(select(User).where(User.id.in_(actor_ids)))} if actor_ids else {}

    activity_ids = {n.activity_id for n in rows if n.activity_id is not None}
    activities = (
        {a.id: a for a in db.scalars(select(Activity).where(Activity.id.in_(activity_ids)))}
        if activity_ids
        else {}
    )
    content_ids = {a.content_id for a in activities.values() if a.content_id is not None}
    contents = (
        {c.id: c for c in db.scalars(select(Content).where(Content.id.in_(content_ids)))}
        if content_ids
        else {}
    )

    comment_ids = {n.comment_id for n in rows if n.comment_id is not None}
    comments = (
        {c.id: c for c in db.scalars(select(ActivityComment).where(ActivityComment.id.in_(comment_ids)))}
        if comment_ids
        else {}
    )

    items = []
    for notification in rows:
        activity = activities.get(notification.activity_id) if notification.activity_id else None
        content = contents.get(activity.content_id) if activity and activity.content_id in contents else None
        comment = comments.get(notification.comment_id) if notification.comment_id else None
        items.append(
            NotificationOut(
                id=notification.id,
                type=notification.type,
                actor=PublicUserOut.model_validate(actors[notification.actor_id]),
                activity_id=notification.activity_id,
                content=catalog_service.content_to_summary(content) if content else None,
                comment_excerpt=_make_excerpt(comment.body, 100)[0] if comment else None,
                is_read=notification.is_read,
                created_at=notification.created_at,
            )
        )
    return CursorPage(items=items, next_cursor=next_cursor)


def unread_notifications_count(db: Session, *, user: User) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.recipient_id == user.id, Notification.is_read.is_(False))
        )
        or 0
    )


def mark_all_notifications_read(db: Session, *, user: User) -> None:
    db.execute(
        update(Notification)
        .where(Notification.recipient_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()


def mark_notification_read(db: Session, *, user: User, notification_id: int) -> None:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.recipient_id != user.id:
        raise not_found("Bildirim bulunamadı")
    notification.is_read = True
    db.commit()


def _review_to_out(
    db: Session, *, review: Review, author: User, content: Content, viewer: User | None
) -> ReviewOut:
    excerpt, is_truncated = _make_excerpt(review.body)
    activity = db.scalar(
        select(Activity).where(
            Activity.actor_id == review.user_id,
            Activity.content_id == review.content_id,
            Activity.verb == "log",
        )
    )
    likes_count = 0
    liked_by_me = False
    comments_count = 0
    if activity is not None:
        likes_count = _count(db, ActivityLike, activity_id=activity.id)
        comments_count = _count(db, ActivityComment, activity_id=activity.id)
        if viewer is not None:
            liked_by_me = db.get(ActivityLike, (activity.id, viewer.id)) is not None

    rating = db.scalar(
        select(LibraryEntry.rating).where(
            LibraryEntry.user_id == review.user_id, LibraryEntry.content_id == review.content_id
        )
    )

    return ReviewOut(
        id=review.id,
        author=PublicUserOut.model_validate(author),
        content=catalog_service.content_to_summary(content),
        body=review.body,
        excerpt=excerpt,
        is_truncated=is_truncated,
        has_spoiler=review.has_spoiler,
        rating=rating,
        created_at=review.created_at,
        updated_at=review.updated_at,
        is_edited=review.updated_at > review.created_at,
        activity_id=activity.id if activity else None,
        likes_count=likes_count,
        liked_by_me=liked_by_me,
        comments_count=comments_count,
    )


def list_content_reviews(
    db: Session,
    *,
    content_type: str,
    external_id: str,
    sort: str,
    page: int,
    viewer: User | None,
    page_size: int = 20,
) -> Page[ReviewOut]:
    content = catalog_service.get_or_create_content(db, content_type, external_id)
    base = select(Review, User).join(User, User.id == Review.user_id).where(Review.content_id == content.id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0

    if sort == "popular":
        rows = db.execute(base).all()
        items = [_review_to_out(db, review=r, author=u, content=content, viewer=viewer) for r, u in rows]
        items.sort(key=lambda r: r.likes_count, reverse=True)
        items = items[(page - 1) * page_size : page * page_size]
    else:
        rows = db.execute(
            base.order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()
        items = [_review_to_out(db, review=r, author=u, content=content, viewer=viewer) for r, u in rows]

    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


def get_review_detail(db: Session, *, review_id: int, viewer: User | None) -> ReviewDetail:
    review = db.get(Review, review_id)
    if review is None:
        raise not_found("İnceleme bulunamadı")
    author = db.get(User, review.user_id)
    content = db.get(Content, review.content_id)
    out = _review_to_out(db, review=review, author=author, content=content, viewer=viewer)
    return ReviewDetail(**out.model_dump())


def list_user_reviews(
    db: Session, *, username: str, page: int, viewer: User | None, page_size: int = 20
) -> Page[ReviewOut]:
    target = db.scalar(select(User).where(User.username == username.lower()))
    if target is None:
        raise not_found("Kullanıcı bulunamadı")

    base = (
        select(Review, Content)
        .join(Content, Content.id == Review.content_id)
        .where(Review.user_id == target.id)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    items = [_review_to_out(db, review=r, author=target, content=c, viewer=viewer) for r, c in rows]
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)
