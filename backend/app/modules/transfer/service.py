import csv
import io
import logging
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from time import monotonic

import httpx
from sqlalchemy import Connection, Engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError, conflict, not_found
from app.core.http import throttled
from app.modules.catalog import service as catalog_service
from app.modules.catalog.models import Content
from app.modules.catalog.schemas import ContentSummary
from app.modules.library import service as library_service
from app.modules.library.models import LibraryEntry, Review
from app.modules.library.schemas import EntryUpdateIn
from app.modules.lists.models import ListItem, UserList
from app.modules.transfer.models import ImportJob
from app.modules.transfer.parsers import ImportRow, ParsedFile, parse_goodreads, parse_letterboxd
from app.modules.transfer.schemas import ImportJobOut, ImportReport, ImportSource, ImportStatus
from app.modules.users.models import User

logger = logging.getLogger(__name__)

MAX_IMPORT_FILE_BYTES = 5 * 1024 * 1024
IMPORT_REQUESTS_PER_SECOND = 3.0
PROGRESS_EVERY_ROWS = 10
# Satır başına ~1 sn sürdüğünden (hız sınırı) küçük dosyada çubuk "0 / 12"de donuk kalmasın
PROGRESS_EVERY_SECONDS = 3.0
MAX_CONSECUTIVE_ERRORS = 5
# İş arka planda (aynı süreçte) koşar; sunucu yeniden başlarsa yarıda kalır. Bu süre boyunca hiç
# ilerleme yazmamış "çalışıyor" görünen iş ölü sayılır, kullanıcı yeni içe aktarma başlatabilir.
STALE_JOB_AFTER = timedelta(minutes=30)

_ACTIVE_STATUSES = (ImportStatus.PENDING.value, ImportStatus.RUNNING.value)
_STATUS_RANK = {"planned": 0, "in_progress": 1, "dropped": 1, "completed": 2}


# --- Dışa aktarma ---


def _iso(value: date | datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _content_ref(content: Content) -> dict:
    return {
        "type": content.type,
        "source": content.source,
        "external_id": content.external_id,
        "title": content.title,
        "year": content.year,
    }


def _library_rows(db: Session, *, user_id: int) -> list[tuple[LibraryEntry, Content]]:
    rows = db.execute(
        select(LibraryEntry, Content)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(LibraryEntry.user_id == user_id)
        .order_by(LibraryEntry.id)
    ).all()
    return [(entry, content) for entry, content in rows]


def _review_rows(db: Session, *, user_id: int) -> list[tuple[Review, Content]]:
    rows = db.execute(
        select(Review, Content)
        .join(Content, Content.id == Review.content_id)
        .where(Review.user_id == user_id)
        .order_by(Review.id)
    ).all()
    return [(review, content) for review, content in rows]


def export_json(db: Session, *, user: User) -> dict:
    lists = db.scalars(select(UserList).where(UserList.user_id == user.id).order_by(UserList.id)).all()
    items_by_list: dict[int, list[dict]] = defaultdict(list)
    if lists:
        item_rows = db.execute(
            select(ListItem, Content)
            .join(Content, Content.id == ListItem.content_id)
            .where(ListItem.list_id.in_([lst.id for lst in lists]))
            .order_by(ListItem.list_id, ListItem.position)
        ).all()
        for item, content in item_rows:
            items_by_list[item.list_id].append(
                {
                    "content": _content_ref(content),
                    "position": item.position,
                    "note": item.note,
                    "added_at": _iso(item.added_at),
                }
            )

    return {
        "format": "kfdu-export",
        "version": 1,
        "exported_at": datetime.now(UTC).isoformat(),
        "profile": {
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio,
            "favorite_genres": user.favorite_genres,
            "created_at": _iso(user.created_at),
        },
        "library": [
            {
                "content": _content_ref(content),
                "status": entry.status,
                "rating": entry.rating,
                "is_favorite": entry.is_favorite,
                "progress": entry.progress,
                "started_at": _iso(entry.started_at),
                "finished_at": _iso(entry.finished_at),
                "rated_at": _iso(entry.rated_at),
                "updated_at": _iso(entry.updated_at),
            }
            for entry, content in _library_rows(db, user_id=user.id)
        ],
        "reviews": [
            {
                "content": _content_ref(content),
                "body": review.body,
                "has_spoiler": review.has_spoiler,
                "created_at": _iso(review.created_at),
                "updated_at": _iso(review.updated_at),
            }
            for review, content in _review_rows(db, user_id=user.id)
        ],
        "lists": [
            {
                "title": lst.title,
                "description": lst.description,
                "is_public": lst.is_public,
                "created_at": _iso(lst.created_at),
                "items": items_by_list[lst.id],
            }
            for lst in lists
        ],
    }


CSV_COLUMNS = (
    "type",
    "title",
    "year",
    "source",
    "external_id",
    "status",
    "rating",
    "favorite",
    "started_at",
    "finished_at",
    "review",
)
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_text(value: str | None) -> str:
    # Excel/Sheets "=..." ile başlayan hücreyi formül olarak çalıştırır (CSV injection); başlıklar
    # Open Library gibi herkesin düzenleyebildiği kaynaklardan geldiği için metin hücreleri etkisizleştirilir.
    if not value:
        return ""
    return f"'{value}" if value.startswith(_FORMULA_PREFIXES) else value


def export_csv(db: Session, *, user: User) -> str:
    # Kütüphanede olmayan ama incelemesi olan içerik de dosyada bir satır olarak yer alır
    contents: dict[int, Content] = {}
    entries: dict[int, LibraryEntry] = {}
    reviews: dict[int, Review] = {}
    for entry, content in _library_rows(db, user_id=user.id):
        contents[content.id], entries[content.id] = content, entry
    for review, content in _review_rows(db, user_id=user.id):
        contents[content.id], reviews[content.id] = content, review

    output = io.StringIO()
    output.write("﻿")  # Excel'in Türkçe karakterleri doğru göstermesi için UTF-8 BOM
    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)
    for content in sorted(contents.values(), key=lambda c: (c.type, c.title.casefold(), c.id)):
        entry = entries.get(content.id)
        review = reviews.get(content.id)
        writer.writerow(
            [
                content.type,
                _csv_text(content.title),
                content.year or "",
                content.source,
                content.external_id,
                (entry.status if entry else None) or "",
                (entry.rating if entry else None) or "",
                "true" if entry is not None and entry.is_favorite else "false",
                _iso(entry.started_at if entry else None) or "",
                _iso(entry.finished_at if entry else None) or "",
                _csv_text(review.body if review else None),
            ]
        )
    return output.getvalue()


def export_filename(user: User, extension: str) -> str:
    # library modülünün "bugün"üyle (date.today()) aynı takvim günü
    return f"kfdu-{user.username}-{date.today().isoformat()}.{extension}"


# --- İçe aktarma: iş oluşturma ve sorgulama ---


def _fail_if_stale(db: Session, job: ImportJob) -> None:
    if job.status in _ACTIVE_STATUSES and datetime.now(UTC) - job.updated_at > STALE_JOB_AFTER:
        job.status = ImportStatus.FAILED.value
        job.error = (
            "İçe aktarma yarıda kesildi. Eşleşenler kütüphanene eklendi; dosyayı yeniden yükleyebilirsin."
        )
        job.finished_at = datetime.now(UTC)
        db.commit()


def start_import(
    db: Session, *, user: User, source: ImportSource, filename: str | None, content: bytes
) -> tuple[ImportJob, ParsedFile]:
    if len(content) > MAX_IMPORT_FILE_BYTES:
        raise AppError(422, "FILE_TOO_LARGE", "Dosya en fazla 5 MB olabilir")
    if source == ImportSource.LETTERBOXD and not settings.TMDB_API_KEY:
        raise AppError(
            503,
            "TMDB_NOT_CONFIGURED",
            "Film verileri için TMDB anahtarı yapılandırılmamış; Letterboxd içe aktarımı şu an kapalı",
        )

    active_jobs = db.scalars(
        select(ImportJob).where(ImportJob.user_id == user.id, ImportJob.status.in_(_ACTIVE_STATUSES))
    ).all()
    for active in active_jobs:
        _fail_if_stale(db, active)
        if active.status in _ACTIVE_STATUSES:
            raise conflict(
                "IMPORT_IN_PROGRESS", "Devam eden bir içe aktarman var; bitince yeni dosya yükleyebilirsin"
            )

    parsed = (
        parse_letterboxd(content, filename) if source == ImportSource.LETTERBOXD else parse_goodreads(content)
    )
    if not parsed.rows:
        raise AppError(422, "EMPTY_IMPORT_FILE", "Dosyada içe aktarılacak satır bulunamadı")

    job = ImportJob(
        user_id=user.id,
        source=source.value,
        status=ImportStatus.PENDING.value,
        total=len(parsed.rows),
        report={"file_kind": parsed.kind.value, "unmatched": []},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job, parsed


def get_import_job(db: Session, *, user: User, job_id: int) -> ImportJob:
    job = db.get(ImportJob, job_id)
    if job is None or job.user_id != user.id:
        raise not_found("İçe aktarma işi bulunamadı")
    _fail_if_stale(db, job)
    return job


def job_to_out(job: ImportJob) -> ImportJobOut:
    report = job.report or {}
    return ImportJobOut(
        id=job.id,
        source=job.source,
        status=job.status,
        total=job.total,
        processed=job.processed,
        matched=job.matched,
        report=ImportReport(file_kind=report.get("file_kind"), unmatched=report.get("unmatched", [])),
        error=job.error,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


# --- İçe aktarma: arka plan işi ---


def _midnight_utc(day: date | None) -> datetime | None:
    return datetime.combine(day, time.min, tzinfo=UTC) if day else None


def _apply_row(db: Session, *, user: User, content_type: str, external_id: str, row: ImportRow) -> None:
    content = catalog_service.get_or_create_content(db, content_type, external_id)
    existing = db.scalar(
        select(LibraryEntry).where(LibraryEntry.user_id == user.id, LibraryEntry.content_id == content.id)
    )

    # İçe aktarma birleştirir, ezmez: puan yalnız boşsa yazılır; durum yalnız ileri gidiyorsa
    # (ör. "İzleyeceğim" → "İzledim") değişir, "İzledim" asla izleme listesiyle geri alınmaz.
    changes: dict[str, object] = {}
    if row.status and (
        existing is None
        or existing.status is None
        or _STATUS_RANK[row.status] > _STATUS_RANK[existing.status]
    ):
        changes["status"] = row.status
    if row.rating and (existing is None or existing.rating is None):
        changes["rating"] = row.rating
    if not changes:
        return

    had_finish_date = existing is not None and existing.finished_at is not None
    library_service.upsert_entry(
        db,
        user=user,
        content_type=content_type,
        external_id=external_id,
        data=EntryUpdateIn(**changes),
        silent=True,
    )

    # upsert_entry tarihleri "bugün/şimdi" diye damgalar. Geçmişten gelen kayıtta dosyadaki tarih esas
    # alınır, bilinmiyorsa boş kalır — yoksa yıllık istatistik, hedef ve özet içe aktarılan her şeyi
    # bu yıla sayar, platformun "son 30 gün popüler" vitrini de tek kullanıcının arşiviyle dolardı.
    entry = db.scalar(
        select(LibraryEntry).where(LibraryEntry.user_id == user.id, LibraryEntry.content_id == content.id)
    )
    if entry is None:
        return
    if changes.get("status") == "completed" and not had_finish_date:
        entry.finished_at = row.finished_on
    if "rating" in changes:
        entry.rated_at = _midnight_utc(row.finished_on or row.logged_on)
    if existing is None and row.logged_on:
        entry.created_at = _midnight_utc(row.logged_on)
    db.commit()


def _matcher(source: str) -> tuple[str, Callable[[ImportRow], ContentSummary | None]]:
    if source == ImportSource.LETTERBOXD.value:
        return "movie", lambda row: catalog_service.find_movie(row.title, row.year)
    return "book", lambda row: catalog_service.find_book(isbns=row.isbns, title=row.title, author=row.author)


class _SourceUnavailable(Exception):
    """Dış kaynak art arda hata veriyor; kalan satırları boşuna denemek yerine iş durdurulur."""


def _process_rows(db: Session, *, job: ImportJob, user: User, rows: list[ImportRow]) -> None:
    content_type, match = _matcher(job.source)
    matched = 0
    unmatched: list[str] = []
    consecutive_errors = 0
    last_saved_at = monotonic()

    def save_progress(processed: int) -> None:
        nonlocal last_saved_at
        job.processed = processed
        job.matched = matched
        job.report = {**job.report, "unmatched": list(unmatched)}
        db.commit()
        last_saved_at = monotonic()

    for index, row in enumerate(rows, start=1):
        try:
            summary = match(row)
            if summary is None:
                unmatched.append(row.label)
            else:
                _apply_row(db, user=user, content_type=content_type, external_id=summary.external_id, row=row)
                matched += 1
            consecutive_errors = 0
        except (AppError, httpx.HTTPError):
            # Tek satırdaki dış servis hatası tüm işi durdurmasın; ama kaynak tamamen çöktüyse
            # binlerce satırı boşuna "eşleşmedi" saymak yerine iş anlaşılır bir hatayla biter.
            db.rollback()
            unmatched.append(row.label)
            consecutive_errors += 1
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                save_progress(index)
                raise _SourceUnavailable from None

        if (
            index % PROGRESS_EVERY_ROWS == 0
            or index == len(rows)
            or monotonic() - last_saved_at >= PROGRESS_EVERY_SECONDS
        ):
            save_progress(index)


def run_import_job(bind: Engine | Connection, job_id: int, rows: list[ImportRow]) -> None:
    """Yanıt gönderildikten sonra BackgroundTasks ile çalışır.

    İsteğin oturumu o sırada kapanmış olduğundan kendi oturumunu, isteğinkiyle AYNI veritabanı
    bağlantısı (bind) üzerinde açar — testlerdeki bellek içi veritabanı da böylece görülür.
    """
    with Session(bind=bind, autoflush=False) as db:
        job = db.get(ImportJob, job_id)
        user = db.get(User, job.user_id) if job is not None else None
        if job is None or user is None:
            return
        job.status = ImportStatus.RUNNING.value
        db.commit()

        try:
            with throttled(IMPORT_REQUESTS_PER_SECOND):
                _process_rows(db, job=job, user=user, rows=rows)
            job.status = ImportStatus.DONE.value
        except _SourceUnavailable:
            job.status = ImportStatus.FAILED.value
            job.error = (
                "Film/kitap veri kaynağı şu anda yanıt vermiyor. Eşleşenler kütüphanene eklendi; "
                "biraz sonra dosyayı yeniden yükleyerek kalanları tamamlayabilirsin."
            )
        except Exception:
            logger.exception("İçe aktarma işi başarısız oldu (job_id=%s)", job_id)
            db.rollback()
            failed_job = db.get(ImportJob, job_id)
            if failed_job is None:  # kullanıcı bu arada hesabını silmiş olabilir
                return
            job = failed_job
            job.status = ImportStatus.FAILED.value
            job.error = (
                "İçe aktarma beklenmedik bir hatayla durdu. Eşleşenler kütüphanene eklendi; "
                "dosyayı yeniden yükleyerek kalanları tamamlayabilirsin."
            )
        job.finished_at = datetime.now(UTC)
        db.commit()
