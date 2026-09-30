from fastapi import APIRouter, Query

from app.core.deps import DbSession
from app.core.errors import not_found
from app.core.pagination import Page
from app.modules.catalog import service
from app.modules.catalog.schemas import (
    AuthorDetail,
    ContentDetail,
    ContentSummary,
    ContentType,
    GenreOut,
    PersonDetail,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search", response_model=Page[ContentSummary], summary="İçerik ara")
def search_content(
    type: ContentType,
    q: str = Query(min_length=1),
    page: int = Query(1, ge=1),
) -> Page[ContentSummary]:
    return service.search(type.value, q, page)


@router.get("/discover", response_model=Page[ContentSummary], summary="İçerik keşfet")
def discover_content(
    type: ContentType,
    genre: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    sort: str = "popular",
    language: str | None = None,
    page: int = Query(1, ge=1),
) -> Page[ContentSummary]:
    return service.discover(
        type.value,
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        sort=sort,
        language=language,
        page=page,
    )


@router.get("/trending", response_model=list[ContentSummary], summary="Haftalık trend")
def trending_content(type: ContentType) -> list[ContentSummary]:
    return service.trending(type.value)


@router.get("/collections/{name}", response_model=list[ContentSummary], summary="Vizyondakiler / yakında")
def collections(name: str) -> list[ContentSummary]:
    return service.collection(name)


@router.get("/genres", response_model=list[GenreOut], summary="Tür listesi")
def genre_list(type: ContentType) -> list[GenreOut]:
    return service.genres(type.value)


@router.get("/people/{person_id}", response_model=PersonDetail, summary="Kişi detayı")
def get_person(person_id: str) -> PersonDetail:
    return service.get_person(person_id)


@router.get("/authors/{author_id}", response_model=AuthorDetail, summary="Yazar detayı")
def get_author(author_id: str) -> AuthorDetail:
    return service.get_author(author_id)


@router.get("/{type}/{external_id}", response_model=ContentDetail, summary="İçerik detayı")
def get_content_detail(type: ContentType, external_id: str, db: DbSession) -> ContentDetail:
    return service.get_detail(db, type.value, external_id)


@router.get("/{type}/{external_id}/similar", response_model=list[ContentSummary], summary="Benzer içerikler")
def similar_content(type: ContentType, external_id: str) -> list[ContentSummary]:
    return service.similar(type.value, external_id)


@router.get(
    "/book/{external_id}/adaptations", response_model=list[ContentSummary], summary="Kitabın uyarlamaları"
)
def get_book_adaptations(external_id: str, db: DbSession) -> list[ContentSummary]:
    return service.get_book_adaptations(db, external_id)


@router.get("/{type}/{external_id}/source-book", response_model=ContentSummary, summary="Uyarlandığı kitap")
def get_source_book(type: ContentType, external_id: str, db: DbSession) -> ContentSummary:
    result = service.get_source_book(db, type.value, external_id)
    if result is None:
        raise not_found("Kaynak kitap bulunamadı")
    return result
