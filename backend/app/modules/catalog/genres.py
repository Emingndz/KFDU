from app.core.genres import GENRE_LABELS, GENRE_TABLE

_TURKISH_FOLD = str.maketrans(
    {
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ı": "i",
        "I": "i",
        "İ": "i",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
    }
)


def label(key: str) -> str:
    return GENRE_LABELS.get(key, key)


def from_tmdb_ids(ids: list[int], content_type: str) -> list[str]:
    attr = "tmdb_movie_id" if content_type == "movie" else "tmdb_tv_id"
    id_set = set(ids)
    return [g.key for g in GENRE_TABLE if getattr(g, attr) in id_set]


def to_tmdb_ids(keys: list[str], content_type: str) -> list[int]:
    attr = "tmdb_movie_id" if content_type == "movie" else "tmdb_tv_id"
    by_key = {g.key: g for g in GENRE_TABLE}
    ids = []
    for key in keys:
        entry = by_key.get(key)
        value = getattr(entry, attr, None) if entry else None
        if value is not None:
            ids.append(value)
    return ids


def from_ol_subjects(subjects: list[str]) -> list[str]:
    normalized = {s.lower().replace(" ", "_") for s in subjects}
    return [g.key for g in GENRE_TABLE if g.ol_subject and g.ol_subject in normalized]


def to_ol_subject(key: str) -> str | None:
    by_key = {g.key: g for g in GENRE_TABLE}
    entry = by_key.get(key)
    return entry.ol_subject if entry else None


def normalize_title(value: str) -> str:
    return value.translate(_TURKISH_FOLD).lower().strip()
