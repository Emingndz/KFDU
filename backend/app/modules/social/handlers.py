from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import events
from app.modules.social.models import Activity, Notification

STATUS_ACTIVITY_REOPEN_WINDOW = timedelta(minutes=60)


def _get_log_activity(db: Session, *, actor_id: int, content_id: int) -> Activity | None:
    return db.scalar(
        select(Activity).where(
            Activity.actor_id == actor_id, Activity.content_id == content_id, Activity.verb == "log"
        )
    )


def _on_library_log_changed(db: Session, *, user_id: int, content_id: int, silent: bool = False) -> None:
    if silent:
        return
    activity = _get_log_activity(db, actor_id=user_id, content_id=content_id)
    if activity is not None:
        activity.updated_at = datetime.now(UTC)
        return
    db.add(Activity(actor_id=user_id, verb="log", content_id=content_id))


def _on_library_log_removed(db: Session, *, user_id: int, content_id: int) -> None:
    activity = _get_log_activity(db, actor_id=user_id, content_id=content_id)
    if activity is not None:
        db.delete(activity)


def _on_library_status_changed(
    db: Session, *, user_id: int, content_id: int, status: str | None, silent: bool = False
) -> None:
    if silent:
        return
    cutoff = datetime.now(UTC) - STATUS_ACTIVITY_REOPEN_WINDOW
    recent = db.scalar(
        select(Activity)
        .where(
            Activity.actor_id == user_id,
            Activity.content_id == content_id,
            Activity.verb == "status",
            Activity.created_at >= cutoff,
        )
        .order_by(Activity.created_at.desc())
    )
    if recent is not None:
        recent.status = status
        recent.updated_at = datetime.now(UTC)
        return
    db.add(Activity(actor_id=user_id, verb="status", content_id=content_id, status=status))


def _on_users_followed(db: Session, *, follower_id: int, followed_id: int) -> None:
    if follower_id == followed_id:
        return
    existing = db.scalar(
        select(Notification).where(
            Notification.recipient_id == followed_id,
            Notification.actor_id == follower_id,
            Notification.type == "follow",
            Notification.is_read.is_(False),
        )
    )
    if existing is not None:
        return
    db.add(Notification(recipient_id=followed_id, actor_id=follower_id, type="follow"))


def _on_lists_created(db: Session, *, user_id: int, list_id: int, is_public: bool) -> None:
    if not is_public:
        return
    db.add(Activity(actor_id=user_id, verb="list_create", list_id=list_id))


def _on_lists_item_added(
    db: Session, *, user_id: int, list_id: int, content_id: int, is_public: bool
) -> None:
    if not is_public:
        return
    existing = db.scalar(
        select(Activity).where(
            Activity.verb == "list_add", Activity.list_id == list_id, Activity.content_id == content_id
        )
    )
    if existing is not None:
        return
    db.add(Activity(actor_id=user_id, verb="list_add", list_id=list_id, content_id=content_id))


def _on_lists_item_removed(db: Session, *, list_id: int, content_id: int) -> None:
    activity = db.scalar(
        select(Activity).where(
            Activity.verb == "list_add", Activity.list_id == list_id, Activity.content_id == content_id
        )
    )
    if activity is not None:
        db.delete(activity)


def _on_lists_visibility_changed(db: Session, *, list_id: int, is_public: bool) -> None:
    if is_public:
        return
    for activity in db.scalars(select(Activity).where(Activity.list_id == list_id)):
        db.delete(activity)


def register_handlers() -> None:
    events.subscribe("library.log_changed", _on_library_log_changed)
    events.subscribe("library.log_removed", _on_library_log_removed)
    events.subscribe("library.status_changed", _on_library_status_changed)
    events.subscribe("users.followed", _on_users_followed)
    events.subscribe("lists.created", _on_lists_created)
    events.subscribe("lists.item_added", _on_lists_item_added)
    events.subscribe("lists.item_removed", _on_lists_item_removed)
    events.subscribe("lists.visibility_changed", _on_lists_visibility_changed)
