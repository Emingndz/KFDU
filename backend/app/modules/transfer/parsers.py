"""Letterboxd / Goodreads dışa aktarma CSV'lerini ortak `ImportRow` biçimine çevirir.

Saf fonksiyonlardır (HTTP ve veritabanı yok); eşleştirme ve kaydetme `service.py`'de yapılır.
"""

import csv
import html
import io
import re
import zipfile
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import PurePosixPath

from app.core.errors import AppError
from app.modules.transfer.schemas import ImportFileKind

STATUS_RANK = {"planned": 0, "in_progress": 1, "dropped": 1, "completed": 2}
# KFDU incelemesi en fazla 5000 karakter (library.schemas.ReviewCreateIn) ve en az 3 karakter olabilir
REVIEW_MIN_CHARS = 3
REVIEW_MAX_CHARS = 5000
# ZIP bombasına karşı: arşivden okunan her CSV ve hepsinin toplamı bu sınırı aşamaz
MAX_ARCHIVE_MEMBER_BYTES = 10 * 1024 * 1024
MAX_ARCHIVE_TOTAL_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True)
class ImportRow:
    title: str
    year: int | None = None
    author: str | None = None
    isbns: tuple[str, ...] = ()
    status: str | None = None
    rating: int | None = None
    finished_on: date | None = None
    logged_on: date | None = None
    review: str | None = None

    @property
    def label(self) -> str:
        if self.author:
            return f"{self.title} — {self.author}"
        return f"{self.title} ({self.year})" if self.year else self.title


@dataclass(frozen=True)
class ParsedFile:
    kind: ImportFileKind
    rows: list[ImportRow]


def _invalid(message: str) -> AppError:
    return AppError(422, "INVALID_IMPORT_FILE", message)


def _read_csv(content: bytes) -> tuple[set[str], list[dict[str, str]]]:
    if content.startswith(b"PK\x03\x04"):
        raise _invalid("Bu bir ZIP arşivi; önce açıp içindeki CSV dosyasını yükle")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise _invalid("Dosya okunamadı; indirdiğin CSV dosyasını değiştirmeden yükle") from exc

    reader = csv.DictReader(io.StringIO(text))
    try:
        reader.fieldnames = [name.strip() for name in reader.fieldnames or []]
        records = list(reader)
    except csv.Error as exc:
        raise _invalid("Dosya geçerli bir CSV değil") from exc
    return set(reader.fieldnames), records


def _to_int(value: str | None) -> int | None:
    try:
        return int(value.strip()) if value and value.strip() else None
    except ValueError:
        return None


def _parse_date(value: str | None) -> date | None:
    if not value or not value.strip():
        return None
    # Letterboxd: 2024-01-15 · Goodreads: 2024/01/15
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


# --- Letterboxd ---

_LETTERBOXD_REQUIRED = {"Name", "Year"}


def _letterboxd_rating(value: str | None) -> int | None:
    # Letterboxd 0,5–5 yıldız verir (yarım yıldız = 1 puan) → 1–10
    try:
        stars = float(value) if value else 0.0
    except ValueError:
        return None
    return min(10, max(1, round(stars * 2))) if stars > 0 else None


_HTML_BREAK_RE = re.compile(r"<\s*(?:br\s*/?|/p)\s*>", re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def _clean_review(value: str | None) -> str | None:
    # Letterboxd inceleme metinleri <br>, <p>, <i> gibi HTML işaretleri taşıyabilir; KFDU düz metin gösterir
    if not value:
        return None
    text = _HTML_TAG_RE.sub("", _HTML_BREAK_RE.sub("\n", value))
    text = _BLANK_LINES_RE.sub("\n\n", html.unescape(text)).strip()[:REVIEW_MAX_CHARS].strip()
    return text if len(text) >= REVIEW_MIN_CHARS else None


def _merge_rows(first: ImportRow, second: ImportRow) -> ImportRow:
    """Aynı filmin iki kaydını birleştirir.

    En son izleme esas alınır (eşitse `second`); onda olmayan puan / inceleme / tarih eskisinden
    tamamlanır. Durum yalnız ileri gider: izleme listesi kaydı "İzledim"i geri almaz.
    """
    if (first.finished_on or date.min) > (second.finished_on or date.min):
        newer, older = first, second
    else:
        newer, older = second, first
    status = max((first.status, second.status), key=lambda s: STATUS_RANK.get(s or "", -1))
    return replace(
        newer,
        status=status,
        rating=newer.rating or older.rating,
        review=newer.review or older.review,
        finished_on=(newer.finished_on or older.finished_on) if status == "completed" else None,
        logged_on=newer.logged_on or older.logged_on,
    )


def _letterboxd_kind(fields: set[str], filename: str | None) -> ImportFileKind:
    if "Rating" in fields:
        # reviews.csv "Review" taşır; diary.csv ile reviews.csv "Watched Date" taşır, ratings.csv taşımaz
        if "Review" in fields:
            return ImportFileKind.REVIEWS
        return ImportFileKind.DIARY if "Watched Date" in fields else ImportFileKind.RATINGS
    # watched.csv ile watchlist.csv'nin sütunları birebir aynı (Date, Name, Year, Letterboxd URI);
    # ikisini yalnız Letterboxd'un verdiği dosya adı ayırt ettirir.
    if filename and "watchlist" in filename.lower():
        return ImportFileKind.WATCHLIST
    return ImportFileKind.WATCHED


def _row_key(row: ImportRow) -> tuple[str, int | None]:
    return (row.title.casefold(), row.year)


def _add_row(rows: dict[tuple[str, int | None], ImportRow], row: ImportRow) -> None:
    key = _row_key(row)
    previous = rows.get(key)
    rows[key] = _merge_rows(previous, row) if previous is not None else row


# ZIP'te okunan dosyalar; sıra, aynı filmin kayıtlarının hangi sırayla birleştirileceğini belirler.
# comments/likes/lists/profile gibi diğer dosyalar KFDU'da karşılığı olmadığı için yok sayılır.
_LETTERBOXD_ARCHIVE_FILES = ("watched.csv", "ratings.csv", "diary.csv", "reviews.csv", "watchlist.csv")


def _parse_letterboxd_archive(content: bytes) -> ParsedFile:
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise _invalid("ZIP okunamadı; Letterboxd'dan indirdiğin dosyayı değiştirmeden yükle") from exc

    with archive:
        members: dict[str, zipfile.ZipInfo] = {}
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            # Yalnız kökteki dosyalar: deleted/ ve orphaned/ klasörlerindeki eski kayıtlar alınmaz
            if not info.is_dir() and len(path.parts) == 1 and path.name.lower() in _LETTERBOXD_ARCHIVE_FILES:
                members[path.name.lower()] = info
        if not members:
            raise _invalid(
                "Bu ZIP'te Letterboxd verisi bulunamadı. "
                "İçinde ratings.csv, watched.csv, watchlist.csv veya diary.csv olan dosyayı yükle"
            )

        rows: dict[tuple[str, int | None], ImportRow] = {}
        total_bytes = 0
        for name in _LETTERBOXD_ARCHIVE_FILES:
            info = members.get(name)
            if info is None:
                continue
            total_bytes += info.file_size
            if info.file_size > MAX_ARCHIVE_MEMBER_BYTES or total_bytes > MAX_ARCHIVE_TOTAL_BYTES:
                raise _invalid("ZIP'in içindeki dosyalar çok büyük; Letterboxd'un verdiği dosyayı yükle")
            for row in parse_letterboxd(archive.read(info), name).rows:
                _add_row(rows, row)
    return ParsedFile(kind=ImportFileKind.ARCHIVE, rows=list(rows.values()))


def parse_letterboxd(content: bytes, filename: str | None = None) -> ParsedFile:
    if content.startswith(b"PK\x03\x04"):
        return _parse_letterboxd_archive(content)

    fields, records = _read_csv(content)
    if not fields >= _LETTERBOXD_REQUIRED:
        raise _invalid(
            "Bu dosya bir Letterboxd dışa aktarımına benzemiyor. "
            "Letterboxd'un verdiği ZIP'i ya da ratings.csv, watched.csv, watchlist.csv, diary.csv, "
            "reviews.csv dosyalarından birini yükle"
        )

    kind = _letterboxd_kind(fields, filename)
    status = "planned" if kind == ImportFileKind.WATCHLIST else "completed"

    # Günlükte aynı film yeniden izlemelerle birden çok kez geçebilir: en son izleme esas alınır,
    # son kayıtta puan / inceleme yoksa öncekinden korunur.
    rows: dict[tuple[str, int | None], ImportRow] = {}
    for record in records:
        title = (record.get("Name") or "").strip()
        if not title:
            continue
        logged_on = _parse_date(record.get("Date"))
        watched_on = _parse_date(record.get("Watched Date")) or logged_on
        _add_row(
            rows,
            ImportRow(
                title=title,
                year=_to_int(record.get("Year")),
                status=status,
                rating=_letterboxd_rating(record.get("Rating")),
                finished_on=watched_on if status == "completed" else None,
                logged_on=logged_on,
                review=_clean_review(record.get("Review")),
            ),
        )
    return ParsedFile(kind=kind, rows=list(rows.values()))


# --- Goodreads ---

_GOODREADS_REQUIRED = {"Title", "Exclusive Shelf"}
_SHELF_STATUS = {
    "read": "completed",
    "currently-reading": "in_progress",
    "to-read": "planned",
    # Goodreads'te varsayılan değil ama en yaygın özel raf adları
    "did-not-finish": "dropped",
    "dnf": "dropped",
    "abandoned": "dropped",
}
# "Dune (Dune, #1)" → "Dune": seri eki arama eşleşmesini bozuyor
_SERIES_SUFFIX_RE = re.compile(r"\s*\([^()]*#\s*[\d.]+\)\s*$")


def _clean_isbn(value: str | None) -> str | None:
    # Goodreads ISBN'leri Excel için ="9780441013593" biçiminde sarar; boşsa ="" yazar
    cleaned = re.sub(r"[^0-9Xx]", "", value or "").upper()
    return cleaned if len(cleaned) in (10, 13) else None


def parse_goodreads(content: bytes) -> ParsedFile:
    fields, records = _read_csv(content)
    if not fields >= _GOODREADS_REQUIRED:
        raise _invalid(
            "Bu dosya bir Goodreads kütüphane dışa aktarımına benzemiyor. "
            "goodreads_library_export.csv dosyasını yükle"
        )

    rows: list[ImportRow] = []
    for record in records:
        title = _SERIES_SUFFIX_RE.sub("", (record.get("Title") or "").strip())
        if not title:
            continue
        status = _SHELF_STATUS.get((record.get("Exclusive Shelf") or "").strip().lower())
        stars = _to_int(record.get("My Rating"))
        rating = stars * 2 if stars and 1 <= stars <= 5 else None
        if status is None and rating is None:
            continue

        isbns = tuple(
            isbn for isbn in (_clean_isbn(record.get("ISBN13")), _clean_isbn(record.get("ISBN"))) if isbn
        )
        rows.append(
            ImportRow(
                title=title,
                author=(record.get("Author") or "").strip() or None,
                isbns=isbns,
                status=status,
                rating=rating,
                finished_on=_parse_date(record.get("Date Read")) if status == "completed" else None,
                logged_on=_parse_date(record.get("Date Added")),
            )
        )
    return ParsedFile(kind=ImportFileKind.GOODREADS_LIBRARY, rows=rows)
