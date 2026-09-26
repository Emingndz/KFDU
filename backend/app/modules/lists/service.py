from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import events
from app.core.errors import bad_request, forbidden, not_found
from app.core.pagination import Page
from app.modules.catalog import service as catalog_service
from app.modules.catalog.models import Content
from app.modules.lists.models import ListItem, UserList
from app.modules.lists.schemas import ListDetail, ListItemOut, ListOut, ListUpdateIn, MyListOut
from app.modules.users.models import User
from app.modules.users.schemas import PublicUserOut


def _cover_urls_and_count(db: Session, list_id: int) -> tuple[list[str], int]:
    rows = db.execute(
        select(Content.poster_url)
        .join(ListItem, ListItem.content_id == Content.id)
        .where(ListItem.list_id == list_id)
        .order_by(ListItem.position)
    ).all()
    urls = [r[0] for r in rows if r[0]]
    return urls[:4], len(rows)


def _list_to_out(db: Session, user_list: UserList, owner: User) -> ListOut:
    covers, count = _cover_urls_and_count(db, user_list.id)
    return ListOut(
        id=user_list.id,
        owner=PublicUserOut.model_validate(owner),
        title=user_list.title,
        description=user_list.description,
        is_public=user_list.is_public,
        item_count=count,
        cover_urls=covers,
        created_at=user_list.created_at,
        updated_at=user_list.updated_at,
    )


def _get_list_or_404(db: Session, list_id: int) -> UserList:
    user_list = db.get(UserList, list_id)
    if user_list is None:
        raise not_found("Liste bulunamadı")
    return user_list


def _require_owner(user_list: UserList, user: User) -> None:
    if user_list.user_id != user.id:
        raise forbidden("Bu liste sana ait değil")


def create_list(db: Session, *, user: User, title: str, description: str | None, is_public: bool) -> ListOut:
    user_list = UserList(user_id=user.id, title=title, description=description, is_public=is_public)
    db.add(user_list)
    db.flush()
    events.emit("lists.created", db=db, user_id=user.id, list_id=user_list.id, is_public=is_public)
    db.commit()
    db.refresh(user_list)
    return _list_to_out(db, user_list, user)


def get_list_detail(db: Session, *, viewer: User | None, list_id: int) -> ListDetail:
    user_list = _get_list_or_404(db, list_id)
    if not user_list.is_public and (viewer is None or viewer.id != user_list.user_id):
        raise not_found("Liste bulunamadı")

    owner = db.get(User, user_list.user_id)
    base = _list_to_out(db, user_list, owner)

    rows = db.execute(
        select(ListItem, Content)
        .join(Content, Content.id == ListItem.content_id)
        .where(ListItem.list_id == list_id)
        .order_by(ListItem.position)
    ).all()
    items = [
        ListItemOut(
            content=catalog_service.content_to_summary(content),
            note=item.note,
            position=item.position,
            added_at=item.added_at,
        )
        for item, content in rows
    ]
    return ListDetail(**base.model_dump(), items=items)


def update_list(db: Session, *, user: User, list_id: int, payload: ListUpdateIn) -> ListOut:
    user_list = _get_list_or_404(db, list_id)
    _require_owner(user_list, user)
    fields = payload.model_fields_set
    was_public = user_list.is_public

    if "title" in fields and payload.title is not None:
        user_list.title = payload.title
    if "description" in fields:
        user_list.description = payload.description
    if "is_public" in fields and payload.is_public is not None:
        user_list.is_public = payload.is_public

    if "is_public" in fields and user_list.is_public != was_public:
        events.emit("lists.visibility_changed", db=db, list_id=list_id, is_public=user_list.is_public)

    db.commit()
    db.refresh(user_list)
    return _list_to_out(db, user_list, user)


def delete_list(db: Session, *, user: User, list_id: int) -> None:
    user_list = _get_list_or_404(db, list_id)
    _require_owner(user_list, user)
    db.delete(user_list)
    db.commit()


def add_item(
    db: Session, *, user: User, list_id: int, content_type: str, external_id: str, note: str | None
) -> tuple[ListItemOut, bool]:
    user_list = _get_list_or_404(db, list_id)
    _require_owner(user_list, user)
    content = catalog_service.get_or_create_content(db, content_type, external_id)

    existing = db.get(ListItem, (list_id, content.id))
    if existing is not None:
        out = ListItemOut(
            content=catalog_service.content_to_summary(content),
            note=existing.note,
            position=existing.position,
            added_at=existing.added_at,
        )
        return out, False

    max_position = db.scalar(select(func.max(ListItem.position)).where(ListItem.list_id == list_id)) or 0
    item = ListItem(list_id=list_id, content_id=content.id, position=max_position + 1, note=note)
    db.add(item)
    events.emit(
        "lists.item_added",
        db=db,
        user_id=user.id,
        list_id=list_id,
        content_id=content.id,
        is_public=user_list.is_public,
    )
    db.commit()
    db.refresh(item)
    out = ListItemOut(
        content=catalog_service.content_to_summary(content),
        note=item.note,
        position=item.position,
        added_at=item.added_at,
    )
    return out, True


def update_item_note(
    db: Session, *, user: User, list_id: int, content_id: int, note: str | None
) -> ListItemOut:
    user_list = _get_list_or_404(db, list_id)
    _require_owner(user_list, user)
    item = db.get(ListItem, (list_id, content_id))
    if item is None:
        raise not_found("Öğe bulunamadı")

    item.note = note
    db.commit()
    db.refresh(item)
    content = db.get(Content, content_id)
    return ListItemOut(
        content=catalog_service.content_to_summary(content),
        note=item.note,
        position=item.position,
        added_at=item.added_at,
    )


def remove_item(db: Session, *, user: User, list_id: int, content_id: int) -> None:
    user_list = _get_list_or_404(db, list_id)
    _require_owner(user_list, user)
    item = db.get(ListItem, (list_id, content_id))
    if item is not None:
        db.delete(item)
        events.emit("lists.item_removed", db=db, list_id=list_id, content_id=content_id)
        db.commit()


def reorder_items(db: Session, *, user: User, list_id: int, content_ids: list[int]) -> None:
    user_list = _get_list_or_404(db, list_id)
    _require_owner(user_list, user)

    items = db.scalars(select(ListItem).where(ListItem.list_id == list_id)).all()
    existing_ids = {item.content_id for item in items}
    if set(content_ids) != existing_ids or len(content_ids) != len(existing_ids):
        raise bad_request("INVALID_ORDER", "Verilen kimlik kümesi listedeki öğelerle birebir aynı olmalı")

    by_content_id = {item.content_id: item for item in items}
    for position, content_id in enumerate(content_ids, start=1):
        by_content_id[content_id].position = position
    db.commit()


def my_lists(
    db: Session, *, user: User, content_type: str | None, external_id: str | None
) -> list[MyListOut]:
    lists = db.scalars(
        select(UserList).where(UserList.user_id == user.id).order_by(UserList.created_at.desc())
    ).all()

    content_id = None
    if content_type and external_id:
        content = catalog_service.get_or_create_content(db, content_type, external_id)
        content_id = content.id

    contains_ids: set[int] = set()
    if content_id is not None and lists:
        list_ids = [ul.id for ul in lists]
        contains_ids = set(
            db.scalars(
                select(ListItem.list_id).where(
                    ListItem.list_id.in_(list_ids), ListItem.content_id == content_id
                )
            )
        )

    return [
        MyListOut(**_list_to_out(db, ul, user).model_dump(), contains=ul.id in contains_ids) for ul in lists
    ]


def list_user_lists(
    db: Session, *, viewer: User | None, username: str, page: int, page_size: int = 20
) -> Page[ListOut]:
    target = db.scalar(select(User).where(User.username == username.lower()))
    if target is None:
        raise not_found("Kullanıcı bulunamadı")

    base = select(UserList).where(UserList.user_id == target.id)
    if viewer is None or viewer.id != target.id:
        base = base.where(UserList.is_public.is_(True))

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(
        base.order_by(UserList.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    items = [_list_to_out(db, ul, target) for ul in rows]
    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)
