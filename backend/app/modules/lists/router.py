from fastapi import APIRouter, Query, Response, status

from app.core.deps import DbSession
from app.core.pagination import Page
from app.modules.catalog.schemas import ContentType
from app.modules.lists import service
from app.modules.lists.schemas import (
    ListCreateIn,
    ListDetail,
    ListItemIn,
    ListItemNoteIn,
    ListItemOut,
    ListOut,
    ListUpdateIn,
    MyListOut,
    ReorderIn,
)
from app.modules.users.deps import CurrentUser, OptionalUser

router = APIRouter(tags=["lists"])


@router.post("/lists", response_model=ListOut, status_code=status.HTTP_201_CREATED, summary="Liste oluştur")
def create_list(payload: ListCreateIn, user: CurrentUser, db: DbSession) -> ListOut:
    return service.create_list(
        db, user=user, title=payload.title, description=payload.description, is_public=payload.is_public
    )


@router.get("/lists/mine", response_model=list[MyListOut], summary="Kendi listelerim")
def my_lists(
    user: CurrentUser,
    db: DbSession,
    type: ContentType | None = None,
    external_id: str | None = None,
) -> list[MyListOut]:
    return service.my_lists(db, user=user, content_type=type.value if type else None, external_id=external_id)


@router.get("/lists/{list_id}", response_model=ListDetail, summary="Liste detayı")
def get_list_detail(list_id: int, viewer: OptionalUser, db: DbSession) -> ListDetail:
    return service.get_list_detail(db, viewer=viewer, list_id=list_id)


@router.patch("/lists/{list_id}", response_model=ListOut, summary="Listeyi güncelle")
def update_list(list_id: int, payload: ListUpdateIn, user: CurrentUser, db: DbSession) -> ListOut:
    return service.update_list(db, user=user, list_id=list_id, payload=payload)


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Listeyi sil")
def delete_list(list_id: int, user: CurrentUser, db: DbSession) -> None:
    service.delete_list(db, user=user, list_id=list_id)


@router.post("/lists/{list_id}/items", response_model=ListItemOut, summary="Listeye öğe ekle")
def add_item(
    list_id: int, payload: ListItemIn, user: CurrentUser, db: DbSession, response: Response
) -> ListItemOut:
    item, created = service.add_item(
        db,
        user=user,
        list_id=list_id,
        content_type=payload.type.value,
        external_id=payload.external_id,
        note=payload.note,
    )
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return item


@router.patch(
    "/lists/{list_id}/items/{content_id}", response_model=ListItemOut, summary="Öğe notunu güncelle"
)
def update_item_note(
    list_id: int, content_id: int, payload: ListItemNoteIn, user: CurrentUser, db: DbSession
) -> ListItemOut:
    return service.update_item_note(db, user=user, list_id=list_id, content_id=content_id, note=payload.note)


@router.delete(
    "/lists/{list_id}/items/{content_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Öğeyi çıkar"
)
def remove_item(list_id: int, content_id: int, user: CurrentUser, db: DbSession) -> None:
    service.remove_item(db, user=user, list_id=list_id, content_id=content_id)


@router.put("/lists/{list_id}/order", status_code=status.HTTP_204_NO_CONTENT, summary="Sıralamayı güncelle")
def reorder_items(list_id: int, payload: ReorderIn, user: CurrentUser, db: DbSession) -> None:
    service.reorder_items(db, user=user, list_id=list_id, content_ids=payload.content_ids)


@router.get("/users/{username}/lists", response_model=Page[ListOut], summary="Kullanıcının listeleri")
def get_user_lists(
    username: str, viewer: OptionalUser, db: DbSession, page: int = Query(1, ge=1)
) -> Page[ListOut]:
    return service.list_user_lists(db, viewer=viewer, username=username, page=page)
