from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.core.pagination import Page
from app.modules.catalog import genres as genre_utils
from app.modules.catalog import service as catalog_service
from app.modules.catalog.models import Content
from app.modules.catalog.schemas import ContentSummary
from app.modules.library.models import LibraryEntry, Review
from app.modules.lists.models import ListItem, UserList
from app.modules.social.models import Activity, ActivityLike
from app.modules.stats.models import UserGoal
from app.modules.stats.schemas import (
    GenreCount,
    GoalOut,
    GoalUpdateIn,
    MonthlyCount,
    PersonCount,
    ProfileSummaryOut,
    StatsHighlights,
    StatsTotals,
    UserStatsOut,
    WrappedOut,
    WrappedReview,
)
from app.modules.users.models import User

GOAL_MEDIA_TYPES = ("movie", "tv", "book")

BAYES_M = 3
DEFAULT_RATING_MID = 5.5

_FUN_TITLES = {
    "action": "Aksiyon Kahramanı",
    "adventure": "Macera Tutkunu",
    "animation": "Çizgi Film Büyücüsü",
    "comedy": "Kahkaha Ustası",
    "crime": "Suç Masası Dedektifi",
    "documentary": "Gerçeklik Avcısı",
    "drama": "Duygu Avcısı",
    "family": "Aile Sofrası Sakini",
    "fantasy": "Büyülü Diyarların Gezgini",
    "history": "Zaman Yolcusu",
    "horror": "Korku Tüneli Müdavimi",
    "music": "Ritim Tutkunu",
    "mystery": "Gizem Çözücü",
    "romance": "Kalp Hırsızı",
    "science_fiction": "Galaksiler Arası Kâşif",
    "thriller": "Gerilim Bağımlısı",
    "war": "Cephe Tarihçisi",
    "western": "Vahşi Batı Kovboyu",
    "children": "Masal Diyarı Sakini",
    "biography": "Hayat Hikâyesi Meraklısı",
    "philosophy": "Düşünce Yolcusu",
    "psychology": "Zihin Kâşifi",
    "self_help": "Kendini Geliştiren",
    "poetry": "Dize Avcısı",
    "classics": "Klasik Sever",
    "young_adult": "Genç Ruhlu Okur",
    "historical_fiction": "Tarihe Yolculuk Eden",
    "fiction": "Roman Kurdu",
    "graphic_novels": "Panel Gezgini",
    "science": "Meraklı Bilim İnsanı",
    "cooking": "Mutfak Şefi",
}
_DEFAULT_FUN_TITLE = "Meraklı İzleyici / Okur"


def _count(db: Session, model: type, **filters: object) -> int:
    conditions = [getattr(model, key) == value for key, value in filters.items()]
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


def get_profile_summary(db: Session, *, username: str) -> ProfileSummaryOut:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        raise not_found("Kullanıcı bulunamadı")

    def completed(content_type: str) -> int:
        return (
            db.scalar(
                select(func.count())
                .select_from(LibraryEntry)
                .join(Content, Content.id == LibraryEntry.content_id)
                .where(
                    LibraryEntry.user_id == user.id,
                    LibraryEntry.status == "completed",
                    Content.type == content_type,
                )
            )
            or 0
        )

    ratings = (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .where(LibraryEntry.user_id == user.id, LibraryEntry.rating.is_not(None))
        )
        or 0
    )
    favorites = (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .where(LibraryEntry.user_id == user.id, LibraryEntry.is_favorite.is_(True))
        )
        or 0
    )

    return ProfileSummaryOut(
        movies_completed=completed("movie"),
        tv_completed=completed("tv"),
        books_completed=completed("book"),
        ratings=ratings,
        reviews=_count(db, Review, user_id=user.id),
        lists=_count(db, UserList, user_id=user.id),
        favorites=favorites,
    )


def get_top_rated(
    db: Session, *, content_type: str | None, page: int, page_size: int = 20
) -> Page[ContentSummary]:
    base_filter = [LibraryEntry.rating.is_not(None)]
    if content_type:
        base_filter.append(Content.type == content_type)

    overall_avg = db.scalar(
        select(func.avg(LibraryEntry.rating))
        .select_from(LibraryEntry)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(*base_filter)
    )
    overall_c = overall_avg or DEFAULT_RATING_MID

    rows = db.execute(
        select(Content.id, func.avg(LibraryEntry.rating), func.count(LibraryEntry.rating))
        .select_from(LibraryEntry)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(*base_filter)
        .group_by(Content.id)
        .having(func.count(LibraryEntry.rating) >= 1)
    ).all()

    scored = []
    for content_id, avg_rating, vote_count in rows:
        weight = vote_count / (vote_count + BAYES_M)
        score = weight * avg_rating + (1 - weight) * overall_c
        scored.append((content_id, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    total = len(scored)
    page_ids = [content_id for content_id, _ in scored[(page - 1) * page_size : page * page_size]]
    contents = {c.id: c for c in db.scalars(select(Content).where(Content.id.in_(page_ids)))}
    items = [catalog_service.content_to_summary(contents[cid]) for cid in page_ids if cid in contents]

    return Page(items=items, page=page, page_size=page_size, total=total, has_next=page * page_size < total)


def get_popular(db: Session, *, content_type: str | None, days: int, limit: int) -> list[ContentSummary]:
    def compute(since: datetime | None) -> list[tuple[int, int]]:
        entry_where = () if since is None else (LibraryEntry.created_at >= since,)
        review_where = () if since is None else (Review.created_at >= since,)
        item_where = () if since is None else (ListItem.added_at >= since,)

        entry_counts = db.execute(
            select(LibraryEntry.content_id, func.count())
            .where(*entry_where)
            .group_by(LibraryEntry.content_id)
        ).all()
        review_counts = db.execute(
            select(Review.content_id, func.count()).where(*review_where).group_by(Review.content_id)
        ).all()
        item_counts = db.execute(
            select(ListItem.content_id, func.count())
            .join(UserList, UserList.id == ListItem.list_id)
            .where(UserList.is_public.is_(True), *item_where)
            .group_by(ListItem.content_id)
        ).all()

        totals: dict[int, int] = defaultdict(int)
        for content_id, cnt in entry_counts:
            totals[content_id] += cnt
        for content_id, cnt in review_counts:
            totals[content_id] += cnt * 2
        for content_id, cnt in item_counts:
            totals[content_id] += cnt
        return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)

    since = datetime.now(UTC) - timedelta(days=days)
    scored = compute(since)
    if len(scored) < 5:
        scored = compute(None)

    if content_type:
        candidate_ids = [content_id for content_id, _ in scored]
        matching_ids = set(
            db.scalars(select(Content.id).where(Content.type == content_type, Content.id.in_(candidate_ids)))
        )
        scored = [(cid, s) for cid, s in scored if cid in matching_ids]

    top_ids = [content_id for content_id, _ in scored[:limit]]
    contents = {c.id: c for c in db.scalars(select(Content).where(Content.id.in_(top_ids)))}
    return [catalog_service.content_to_summary(contents[cid]) for cid in top_ids if cid in contents]


def _completed_in_year(db: Session, *, user_id: int, year: int):
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    return db.execute(
        select(LibraryEntry, Content)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(
            LibraryEntry.user_id == user_id,
            LibraryEntry.status == "completed",
            LibraryEntry.finished_at.is_not(None),
            LibraryEntry.finished_at >= year_start,
            LibraryEntry.finished_at <= year_end,
        )
    ).all()


def _excerpt(body: str, limit: int = 140) -> str:
    if len(body) <= limit:
        return body
    truncated = body[:limit]
    last_space = truncated.rfind(" ")
    return f"{truncated[:last_space] if last_space > 0 else truncated}…"


def get_user_stats(db: Session, *, username: str, year: int | None = None) -> UserStatsOut:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        raise not_found("Kullanıcı bulunamadı")
    resolved_year = year or datetime.now(UTC).year

    rows = _completed_in_year(db, user_id=user.id, year=resolved_year)

    totals_movies = totals_tv = totals_books = 0
    minutes = pages = 0
    monthly = {m: {"movies": 0, "tv": 0, "books": 0} for m in range(1, 13)}
    genre_counter: Counter[str] = Counter()
    people_counter: Counter[str] = Counter()
    movie_candidates: list[tuple[int, Content]] = []
    book_candidates: list[tuple[int, Content]] = []
    rated_candidates: list[tuple[int, Content]] = []

    for entry, content in rows:
        month = entry.finished_at.month
        if content.type == "movie":
            totals_movies += 1
            monthly[month]["movies"] += 1
            minutes += content.runtime_minutes or 0
            movie_candidates.append((content.runtime_minutes or 0, content))
        elif content.type == "tv":
            totals_tv += 1
            monthly[month]["tv"] += 1
        else:
            totals_books += 1
            monthly[month]["books"] += 1
            pages += content.page_count or 0
            book_candidates.append((content.page_count or 0, content))

        for genre_key in content.genres or []:
            genre_counter[genre_key] += 1

        people = content.people or {}
        for person in people.get("directors", []) + people.get("authors", []):
            if person.get("name"):
                people_counter[person["name"]] += 1

        if entry.rating is not None:
            rated_candidates.append((entry.rating, content))

    year_start_dt = datetime(resolved_year, 1, 1, tzinfo=UTC)
    year_end_dt = datetime(resolved_year + 1, 1, 1, tzinfo=UTC)

    reviews_count = (
        db.scalar(
            select(func.count())
            .select_from(Review)
            .where(
                Review.user_id == user.id,
                Review.created_at >= year_start_dt,
                Review.created_at < year_end_dt,
            )
        )
        or 0
    )
    rating_rows = db.execute(
        select(LibraryEntry.rating, func.count())
        .where(
            LibraryEntry.user_id == user.id,
            LibraryEntry.rating.is_not(None),
            LibraryEntry.rated_at >= year_start_dt,
            LibraryEntry.rated_at < year_end_dt,
        )
        .group_by(LibraryEntry.rating)
    ).all()
    rating_distribution = {int(rating): int(count) for rating, count in rating_rows}
    avg_rating = None
    if rating_distribution:
        total_ratings = sum(rating_distribution.values())
        weighted = sum(rating * count for rating, count in rating_distribution.items())
        avg_rating = round(weighted / total_ratings, 2)

    top_genres = [
        GenreCount(key=key, label=genre_utils.label(key), count=count)
        for key, count in genre_counter.most_common(8)
    ]
    top_people = [PersonCount(name=name, count=count) for name, count in people_counter.most_common(5)]
    monthly_out = [
        MonthlyCount(month=m, movies=monthly[m]["movies"], tv=monthly[m]["tv"], books=monthly[m]["books"])
        for m in range(1, 13)
    ]

    longest_movie = max(movie_candidates, key=lambda pair: pair[0], default=(0, None))[1]
    longest_book = max(book_candidates, key=lambda pair: pair[0], default=(0, None))[1]
    highest_rated = [
        catalog_service.content_to_summary(content)
        for _, content in sorted(rated_candidates, key=lambda pair: pair[0], reverse=True)[:5]
    ]

    return UserStatsOut(
        year=resolved_year,
        totals=StatsTotals(
            movies=totals_movies,
            tv=totals_tv,
            books=totals_books,
            minutes=minutes,
            pages=pages,
            reviews=reviews_count,
            avg_rating=avg_rating,
        ),
        rating_distribution=rating_distribution,
        top_genres=top_genres,
        monthly=monthly_out,
        top_people=top_people,
        highlights=StatsHighlights(
            longest_movie=catalog_service.content_to_summary(longest_movie) if longest_movie else None,
            longest_book=catalog_service.content_to_summary(longest_book) if longest_book else None,
            highest_rated=highest_rated,
        ),
    )


def get_wrapped(db: Session, *, user: User, year: int | None = None) -> WrappedOut:
    resolved_year = year or datetime.now(UTC).year
    stats = get_user_stats(db, username=user.username, year=resolved_year)

    year_start = date(resolved_year, 1, 1)
    year_end = date(resolved_year, 12, 31)
    completed_query = (
        select(LibraryEntry, Content)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(
            LibraryEntry.user_id == user.id,
            LibraryEntry.status == "completed",
            LibraryEntry.finished_at.is_not(None),
            LibraryEntry.finished_at >= year_start,
            LibraryEntry.finished_at <= year_end,
        )
    )
    first_row = db.execute(completed_query.order_by(LibraryEntry.finished_at.asc()).limit(1)).first()
    last_row = db.execute(completed_query.order_by(LibraryEntry.finished_at.desc()).limit(1)).first()
    first_completed = catalog_service.content_to_summary(first_row[1]) if first_row else None
    last_completed = catalog_service.content_to_summary(last_row[1]) if last_row else None

    year_start_dt = datetime(resolved_year, 1, 1, tzinfo=UTC)
    year_end_dt = datetime(resolved_year + 1, 1, 1, tzinfo=UTC)
    review_row = db.execute(
        select(Review, Content, func.count(ActivityLike.activity_id))
        .join(Content, Content.id == Review.content_id)
        .join(
            Activity,
            (Activity.actor_id == Review.user_id)
            & (Activity.content_id == Review.content_id)
            & (Activity.verb == "log"),
        )
        .outerjoin(ActivityLike, ActivityLike.activity_id == Activity.id)
        .where(
            Review.user_id == user.id,
            Review.created_at >= year_start_dt,
            Review.created_at < year_end_dt,
        )
        .group_by(Review.id, Content.id)
        .order_by(func.count(ActivityLike.activity_id).desc())
        .limit(1)
    ).first()
    most_liked_review = None
    if review_row is not None:
        review, content, likes_count = review_row
        most_liked_review = WrappedReview(
            id=review.id,
            content=catalog_service.content_to_summary(content),
            excerpt=_excerpt(review.body),
            likes_count=likes_count,
        )

    most_active = max(stats.monthly, key=lambda m: m.movies + m.tv + m.books, default=None)
    most_active_total = most_active.movies + most_active.tv + most_active.books if most_active else 0
    most_active_month = most_active.month if most_active and most_active_total > 0 else None

    dominant_genre = stats.top_genres[0] if stats.top_genres else None
    fun_title = _FUN_TITLES.get(dominant_genre.key, _DEFAULT_FUN_TITLE) if dominant_genre else None

    return WrappedOut(
        stats=stats,
        first_completed=first_completed,
        last_completed=last_completed,
        most_liked_review=most_liked_review,
        most_active_month=most_active_month,
        dominant_genre=dominant_genre,
        fun_title=fun_title,
    )


def get_goals(db: Session, *, user: User, year: int | None = None) -> list[GoalOut]:
    resolved_year = year or datetime.now(UTC).year
    rows = db.scalars(
        select(UserGoal).where(UserGoal.user_id == user.id, UserGoal.year == resolved_year)
    ).all()
    targets = {g.media_type: g.target for g in rows}

    completed = _completed_in_year(db, user_id=user.id, year=resolved_year)
    current_counts = Counter(content.type for _, content in completed)

    return [
        GoalOut(media_type=mt, target=targets.get(mt, 0), current=current_counts.get(mt, 0))
        for mt in GOAL_MEDIA_TYPES
    ]


def set_goals(db: Session, *, user: User, year: int | None, goals: list[GoalUpdateIn]) -> list[GoalOut]:
    resolved_year = year or datetime.now(UTC).year
    for goal in goals:
        if goal.media_type not in GOAL_MEDIA_TYPES:
            continue
        existing = db.scalar(
            select(UserGoal).where(
                UserGoal.user_id == user.id,
                UserGoal.year == resolved_year,
                UserGoal.media_type == goal.media_type,
            )
        )
        # target<=0 "hedef yok" anlamına gelir — kaydedilmez, zaten var olan satır silinir.
        # Aksi halde bir hedef=0 satırı, current>=0 her zaman doğru olduğu için "goal_getter"
        # rozetini anlamsızca tetikler.
        if goal.target <= 0:
            if existing is not None:
                db.delete(existing)
            continue
        if existing is None:
            db.add(
                UserGoal(user_id=user.id, year=resolved_year, media_type=goal.media_type, target=goal.target)
            )
        else:
            existing.target = goal.target
    db.commit()
    return get_goals(db, user=user, year=resolved_year)
