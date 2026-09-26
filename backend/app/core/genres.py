from dataclasses import dataclass


@dataclass(frozen=True)
class GenreEntry:
    key: str
    label: str
    tmdb_movie_id: int | None
    tmdb_tv_id: int | None
    ol_subject: str | None


GENRE_TABLE: tuple[GenreEntry, ...] = (
    GenreEntry("action", "Aksiyon", 28, 10759, None),
    GenreEntry("adventure", "Macera", 12, 10759, "adventure"),
    GenreEntry("animation", "Animasyon", 16, 16, None),
    GenreEntry("comedy", "Komedi", 35, 35, "humor"),
    GenreEntry("crime", "Suç", 80, 80, "crime"),
    GenreEntry("documentary", "Belgesel", 99, 99, None),
    GenreEntry("drama", "Dram", 18, 18, "drama"),
    GenreEntry("family", "Aile", 10751, 10751, None),
    GenreEntry("fantasy", "Fantastik", 14, 10765, "fantasy"),
    GenreEntry("history", "Tarih", 36, 10768, "history"),
    GenreEntry("horror", "Korku", 27, None, "horror"),
    GenreEntry("music", "Müzik", 10402, None, "music"),
    GenreEntry("mystery", "Gizem / Polisiye", 9648, 9648, "mystery_and_detective_stories"),
    GenreEntry("romance", "Romantik", 10749, None, "romance"),
    GenreEntry("science_fiction", "Bilim Kurgu", 878, 10765, "science_fiction"),
    GenreEntry("thriller", "Gerilim", 53, None, "thriller"),
    GenreEntry("war", "Savaş", 10752, 10768, "war"),
    GenreEntry("western", "Western", 37, 37, "westerns"),
    GenreEntry("children", "Çocuk", None, 10762, "children"),
    GenreEntry("biography", "Biyografi", None, None, "biography"),
    GenreEntry("philosophy", "Felsefe", None, None, "philosophy"),
    GenreEntry("psychology", "Psikoloji", None, None, "psychology"),
    GenreEntry("self_help", "Kişisel Gelişim", None, None, "self-help"),
    GenreEntry("poetry", "Şiir", None, None, "poetry"),
    GenreEntry("classics", "Klasikler", None, None, "classic_literature"),
    GenreEntry("young_adult", "Genç Yetişkin", None, None, "young_adult_fiction"),
    GenreEntry("historical_fiction", "Tarihî Roman", None, None, "historical_fiction"),
    GenreEntry("fiction", "Roman / Edebiyat", None, None, "fiction"),
    GenreEntry("graphic_novels", "Çizgi Roman", None, None, "graphic_novels"),
    GenreEntry("science", "Bilim", None, None, "science"),
    GenreEntry("cooking", "Yemek", None, None, "cooking"),
)

GENRE_LABELS: dict[str, str] = {g.key: g.label for g in GENRE_TABLE}
GENRE_KEYS: frozenset[str] = frozenset(GENRE_LABELS)
