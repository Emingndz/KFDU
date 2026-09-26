import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.modules.catalog.models import Content
from app.modules.library.models import LibraryEntry, Review
from app.modules.users.models import Follow, User


def _make_user(db, username: str, email: str) -> User:
    user = User(username=username, email=email, password_hash="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_content(db, external_id: str) -> Content:
    content = Content(type="movie", source="tmdb", external_id=external_id, title="Test Film")
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def test_duplicate_library_entry_raises_integrity_error(db):
    user = _make_user(db, "user1", "user1@example.com")
    content = _make_content(db, "1")
    db.add(LibraryEntry(user_id=user.id, content_id=content.id, status="planned"))
    db.commit()

    db.add(LibraryEntry(user_id=user.id, content_id=content.id, status="completed"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_rating_out_of_range_raises_integrity_error(db):
    user = _make_user(db, "user2", "user2@example.com")
    content = _make_content(db, "2")
    db.add(LibraryEntry(user_id=user.id, content_id=content.id, rating=11))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_self_follow_raises_integrity_error(db):
    user = _make_user(db, "user3", "user3@example.com")
    db.add(Follow(follower_id=user.id, followed_id=user.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_deleting_user_cascades_entries_and_reviews(db):
    user = _make_user(db, "user4", "user4@example.com")
    content = _make_content(db, "3")
    db.add(LibraryEntry(user_id=user.id, content_id=content.id, status="completed"))
    db.add(Review(user_id=user.id, content_id=content.id, body="Harika bir film, çok beğendim."))
    db.commit()

    db.delete(user)
    db.commit()

    assert db.scalars(select(LibraryEntry).where(LibraryEntry.user_id == user.id)).all() == []
    assert db.scalars(select(Review).where(Review.user_id == user.id)).all() == []
