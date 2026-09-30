from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.modules.catalog.models import Content
from app.modules.library.models import LibraryEntry, Review
from app.modules.lists.models import UserList
from app.modules.stats.models import UserGoal
from app.modules.stats.schemas import BadgeOut, BadgeProgress
from app.modules.users.models import Follow, User


def _completed_count(db: Session, *, user_id: int, media_type: str) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .join(Content, Content.id == LibraryEntry.content_id)
            .where(
                LibraryEntry.user_id == user_id,
                LibraryEntry.status == "completed",
                Content.type == media_type,
            )
        )
        or 0
    )


def _completed_count_for_year(db: Session, *, user_id: int, media_type: str, year: int) -> int:
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    return (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .join(Content, Content.id == LibraryEntry.content_id)
            .where(
                LibraryEntry.user_id == user_id,
                LibraryEntry.status == "completed",
                Content.type == media_type,
                LibraryEntry.finished_at.is_not(None),
                LibraryEntry.finished_at >= year_start,
                LibraryEntry.finished_at <= year_end,
            )
        )
        or 0
    )


def _ratings_count(db: Session, *, user_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(LibraryEntry)
            .where(LibraryEntry.user_id == user_id, LibraryEntry.rating.is_not(None))
        )
        or 0
    )


def _reviews_count(db: Session, *, user_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Review).where(Review.user_id == user_id)) or 0


def _distinct_genres_count(db: Session, *, user_id: int) -> int:
    rows = db.scalars(
        select(Content.genres)
        .select_from(LibraryEntry)
        .join(Content, Content.id == LibraryEntry.content_id)
        .where(LibraryEntry.user_id == user_id, LibraryEntry.status == "completed")
    ).all()
    genres: set[str] = set()
    for row in rows:
        genres.update(row or [])
    return len(genres)


def _following_count(db: Session, *, user_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)) or 0


def _followers_count(db: Session, *, user_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Follow).where(Follow.followed_id == user_id)) or 0


def _lists_count(db: Session, *, user_id: int) -> int:
    return db.scalar(select(func.count()).select_from(UserList).where(UserList.user_id == user_id)) or 0


def _goal_getter_achieved(db: Session, *, user_id: int) -> bool:
    goals = db.scalars(select(UserGoal).where(UserGoal.user_id == user_id)).all()
    for goal in goals:
        if goal.target <= 0:
            continue
        current = _completed_count_for_year(db, user_id=user_id, media_type=goal.media_type, year=goal.year)
        if current >= goal.target:
            return True
    return False


def get_badges(db: Session, *, username: str) -> list[BadgeOut]:
    user = db.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        raise not_found("Kullanıcı bulunamadı")

    movies = _completed_count(db, user_id=user.id, media_type="movie")
    tv = _completed_count(db, user_id=user.id, media_type="tv")
    books = _completed_count(db, user_id=user.id, media_type="book")
    ratings = _ratings_count(db, user_id=user.id)
    reviews = _reviews_count(db, user_id=user.id)
    genres = _distinct_genres_count(db, user_id=user.id)
    following = _following_count(db, user_id=user.id)
    followers = _followers_count(db, user_id=user.id)
    lists = _lists_count(db, user_id=user.id)

    definitions = [
        ("first_step", "İlk Adım", "İlk puanını ver", "Star", ratings, 1),
        ("critic", "Eleştirmen", "10 inceleme yaz", "PenLine", reviews, 10),
        ("cinephile", "Sinefil", "50 film izle", "Clapperboard", movies, 50),
        ("cinephile_pro", "Sinema Kurdu", "200 film izle", "Clapperboard", movies, 200),
        ("bookworm", "Kitap Kurdu", "25 kitap oku", "BookOpen", books, 25),
        ("bookworm_pro", "Kütüphane Faresi", "100 kitap oku", "BookOpen", books, 100),
        ("binge", "Dizi Bağımlısı", "10 dizi bitir", "Tv", tv, 10),
        ("explorer", "Tür Kâşifi", "10 farklı türde içerik tamamla", "Compass", genres, 10),
        ("social", "Sosyal Kelebek", "10 kişiyi takip et", "Users", following, 10),
        ("popular", "Popüler", "10 takipçi kazan", "Heart", followers, 10),
        ("curator", "Küratör", "5 liste oluştur", "ListChecks", lists, 5),
    ]

    badges = [
        BadgeOut(
            key=key,
            name=name,
            description=description,
            icon=icon,
            earned=current >= target,
            progress=BadgeProgress(current=min(current, target), target=target),
        )
        for key, name, description, icon, current, target in definitions
    ]

    goal_getter = _goal_getter_achieved(db, user_id=user.id)
    badges.append(
        BadgeOut(
            key="goal_getter",
            name="Hedef Avcısı",
            description="Bir yıllık hedefini tamamla",
            icon="Target",
            earned=goal_getter,
            progress=BadgeProgress(current=1 if goal_getter else 0, target=1),
        )
    )
    return badges
