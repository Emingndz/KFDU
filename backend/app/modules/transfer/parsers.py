"""Letterboxd / Goodreads dışa aktarma CSV'lerini ortak `ImportRow` biçimine çevirir.

Saf fonksiyonlardır (HTTP ve veritabanı yok); eşleştirme ve kaydetme `service.py`'de yapılır.
"""

import csv
import io
import re
from dataclasses import dataclass, replace
from datetime import date, datetime

from app.core.errors import AppError
from app.modules.transfer.schemas import ImportFileKind


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


def _letterboxd_kind(fields: set[str], filename: str | None) -> ImportFileKind:
    if "Rating" in fields:
        # diary.csv ve reviews.csv "Watched Date" taşır; ratings.csv taşımaz
        return ImportFileKind.DIARY if "Watched Date" in fields else ImportFileKind.RATINGS
    # watched.csv ile watchlist.csv'nin sütunları birebir aynı (Date, Name, Year, Letterboxd URI);
    # ikisini yalnız Letterboxd'un verdiği dosya adı ayırt ettirir.
    if filename and "watchlist" in filename.lower():
        return ImportFileKind.WATCHLIST
    return ImportFileKind.WATCHED


def parse_letterboxd(content: bytes, filename: str | None = None) -> ParsedFile:
    fields, records = _read_csv(content)
    if not fields >= _LETTERBOXD_REQUIRED:
        raise _invalid(
            "Bu dosya bir Letterboxd dışa aktarımına benzemiyor. "
            "ratings.csv, watched.csv, watchlist.csv veya diary.csv dosyalarından birini yükle"
        )

    kind = _letterboxd_kind(fields, filename)
    status = "planned" if kind == ImportFileKind.WATCHLIST else "completed"

    rows: dict[tuple[str, int | None], ImportRow] = {}
    for record in records:
        title = (record.get("Name") or "").strip()
        if not title:
            continue
        year = _to_int(record.get("Year"))
        logged_on = _parse_date(record.get("Date"))
        watched_on = _parse_date(record.get("Watched Date")) or logged_on
        row = ImportRow(
            title=title,
            year=year,
            status=status,
            rating=_letterboxd_rating(record.get("Rating")),
            finished_on=watched_on if status == "completed" else None,
            logged_on=logged_on,
        )

        key = (title.casefold(), year)
        previous = rows.get(key)
        if previous is not None:
            # Günlükte aynı film yeniden izlemelerle birden çok kez geçebilir: en son izleme esas alınır,
            # son kayıtta puan yoksa önceki puan korunur.
            if (previous.finished_on or date.min) > (row.finished_on or date.min):
                row, previous = previous, row
            row = replace(row, rating=row.rating or previous.rating)
        rows[key] = row
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
