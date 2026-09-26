"""Demo verisi yükleyici.

Kullanım:
    python -m scripts.seed            # mevcut veritabanına demo veri ekler
    python -m scripts.seed --reset    # (yalnız ENV=dev) veritabanını sıfırlar, sonra ekler
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.errors import AppError
from app.modules.auth import service as auth_service
from app.modules.catalog import service as catalog_service
from app.modules.catalog.schemas import ContentType
from app.modules.library import service as library_service
from app.modules.library.schemas import EntryUpdateIn, LibraryStatus, ReviewCreateIn
from app.modules.lists import service as lists_service
from app.modules.social import service as social_service
from app.modules.social.handlers import register_handlers
from app.modules.social.models import Activity
from app.modules.users import service as users_service
from app.modules.users.models import User

logger = logging.getLogger(__name__)

DEMO_PASSWORD = "Demo1234!"
DEMO_GENRES = [
    ["action", "science_fiction"],
    ["drama", "romance"],
    ["comedy", "animation"],
    ["fiction", "classics"],
    ["horror", "thriller"],
    ["fantasy", "young_adult"],
]

MOVIE_TITLES = [
    "Inception",
    "Interstellar",
    "The Dark Knight",
    "Parasite",
    "Spirited Away",
    "The Godfather",
    "Kış Uykusu",
    "Babam ve Oğlum",
    "Bir Zamanlar Anadolu'da",
    "Whiplash",
]
BOOK_TITLES = [
    "Suç ve Ceza",
    "1984",
    "Simyacı",
    "Kürk Mantolu Madonna",
    "Tutunamayanlar",
    "Dune",
    "Sefiller",
    "Küçük Prens",
    "Hayvan Çiftliği",
    "Beyaz Diş",
]

REVIEW_BODIES = [
    (
        "Baştan sona sürükleyiciydi; karakterlerin gelişimi çok inandırıcı işlenmiş. "
        "Özellikle ikinci yarıdaki gerilim beni gerçekten etkiledi ve bitirdikten sonra "
        "uzun süre üzerine düşündüm. Kesinlikle tekrar okuyacağım/izleyeceğim eserlerden."
    ),
    (
        "İlk başta biraz yavaş geldi ama sabrettiğime değdi. Anlatım tarzı alışılmadık "
        "ama etkileyici; final sahnesi tüm hikayeyi bambaşka bir yere taşıyor. Herkese "
        "tavsiye edebileceğim, üzerine konuşulması gereken bir eser oldu benim için."
    ),
    "Finaldeki twist gerçekten şoke ediciydi, hiç beklemiyordum. (Spoiler: kahraman aslında hayattaymış.)",
    "Beklediğimden çok daha iyiydi, bir solukta bitirdim.",
    "Tempom biraz yavaş geldi ama sonu her şeye değdi.",
    "Karakterler çok gerçekçi işlenmiş, kendimi içinde buldum.",
    "Görsel/anlatım dili muhteşemdi, tekrar tekrar izlenir/okunur.",
    "Ortalama bir eserdi, fena değildi ama beklentimi karşılamadı.",
    "Yılın en iyilerinden, kesinlikle tavsiye ederim.",
    "Biraz uzun sürdü ama duygusal olarak çok doyurucuydu.",
    "Basit ama etkili bir hikaye, kısa sürede bitirilebilir.",
    "Atmosferi çok başarılı, uzun süre etkisinde kaldım.",
]


def _reset_database() -> None:
    if settings.ENV != "dev":
        print("--reset yalnızca ENV=dev iken kullanılabilir.")
        raise SystemExit(1)

    backend_dir = Path(__file__).resolve().parent.parent
    for suffix in ("", "-shm", "-wal"):
        db_file = backend_dir / f"kfdu.db{suffix}"
        if db_file.exists():
            db_file.unlink()
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True, cwd=backend_dir)
    print("Veritabanı sıfırlandı ve migrationlar uygulandı.")


def _resolve(db: Session, content_type: str, title: str) -> tuple[str, str] | None:
    try:
        page = catalog_service.search(content_type, title, 1)
    except AppError as exc:
        logger.warning("Aranamadı (%s): %s -> %s", content_type, title, exc.message)
        return None
    if not page.items:
        logger.warning("Bulunamadı (%s): %s", content_type, title)
        return None
    return content_type, page.items[0].external_id


def _seed(db: Session) -> None:
    users: list[User] = []
    for i in range(1, 7):
        username = f"demo{i}"
        user = auth_service.register(
            db, username=username, email=f"{username}@kfdu.local", password=DEMO_PASSWORD
        )
        user.favorite_genres = DEMO_GENRES[i - 1]
        db.commit()
        users.append(user)
    print(f"{len(users)} demo kullanıcı oluşturuldu.")

    for i, user in enumerate(users):
        for offset in (1, 2):
            target = users[(i + offset) % len(users)]
            users_service.follow(db, follower=user, username=target.username)
    print("Takip ilişkileri oluşturuldu.")

    resolved: list[tuple[str, str]] = []
    for title in MOVIE_TITLES:
        item = _resolve(db, "movie", title)
        if item:
            resolved.append(item)
    for title in BOOK_TITLES:
        item = _resolve(db, "book", title)
        if item:
            resolved.append(item)
    print(f"{len(resolved)}/{len(MOVIE_TITLES) + len(BOOK_TITLES)} içerik bulundu.")

    if not resolved:
        print("Hiç içerik bulunamadı; kütüphane/inceleme/liste adımları atlanıyor.")
        db.commit()
        return

    statuses = [
        LibraryStatus.COMPLETED,
        LibraryStatus.COMPLETED,
        LibraryStatus.IN_PROGRESS,
        LibraryStatus.PLANNED,
        LibraryStatus.DROPPED,
    ]
    review_bodies = iter(REVIEW_BODIES)
    entry_count = 0
    review_count = 0

    for i, user in enumerate(users):
        for j, (content_type, external_id) in enumerate(resolved):
            if (i + j) % 3 == 2:
                continue
            status_value = statuses[(i + j) % len(statuses)]
            rating = 4 + ((i + j) % 7) if status_value != LibraryStatus.DROPPED else None
            library_service.upsert_entry(
                db,
                user=user,
                content_type=content_type,
                external_id=external_id,
                data=EntryUpdateIn(status=status_value, rating=rating),
            )
            entry_count += 1

            if status_value == LibraryStatus.COMPLETED:
                body = next(review_bodies, None)
                if body is not None:
                    try:
                        library_service.create_review(
                            db,
                            user=user,
                            payload=ReviewCreateIn(
                                type=ContentType(content_type),
                                external_id=external_id,
                                body=body,
                                has_spoiler="Spoiler" in body,
                            ),
                        )
                        review_count += 1
                    except AppError:
                        pass
    print(f"{entry_count} kütüphane girişi, {review_count} inceleme oluşturuldu.")

    list_specs = [
        (users[0], "En Sevdiklerim", True),
        (users[1], "Okuma/İzleme Listem", True),
        (users[2], "Gizli Favorilerim", False),
    ]
    for owner, title, is_public in list_specs:
        list_out = lists_service.create_list(
            db, user=owner, title=title, description=None, is_public=is_public
        )
        for content_type, external_id in resolved[:4]:
            lists_service.add_item(
                db,
                user=owner,
                list_id=list_out.id,
                content_type=content_type,
                external_id=external_id,
                note=None,
            )
    print(f"{len(list_specs)} liste oluşturuldu.")

    activities = db.scalars(select(Activity).where(Activity.verb == "log").limit(10)).all()
    like_count = 0
    comment_count = 0
    for i, activity in enumerate(activities):
        liker = users[(i + 1) % len(users)]
        if liker.id != activity.actor_id:
            social_service.like_activity(db, user=liker, activity_id=activity.id)
            like_count += 1
        commenter = users[(i + 2) % len(users)]
        if commenter.id != activity.actor_id:
            social_service.add_comment(
                db, user=commenter, activity_id=activity.id, body="Güzel seçim, ben de denemek istiyorum."
            )
            comment_count += 1
    print(f"{like_count} beğeni, {comment_count} yorum eklendi.")

    db.commit()
    print("Demo verisi başarıyla yüklendi.")


def run(*, reset: bool) -> None:
    if reset:
        _reset_database()

    register_handlers()
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.username == "demo1")) is not None:
            print("Demo verisi zaten yüklü.")
            return
        _seed(db)
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="KFDU demo verisi yükleyici")
    parser.add_argument(
        "--reset", action="store_true", help="Veritabanını sıfırlayıp yeniden kurar (yalnız ENV=dev)"
    )
    args = parser.parse_args()
    run(reset=args.reset)


if __name__ == "__main__":
    main()
