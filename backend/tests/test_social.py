import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import respx
from httpx import Response
from sqlalchemy import event

from app.modules.library.models import Review
from app.modules.social.models import Activity, ActivityComment, ActivityLike, Notification
from tests.conftest import auth_headers
from tests.conftest import engine as test_engine

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _mock_book_detail() -> None:
    respx.get("https://openlibrary.org/search.json", params={"q": 'key:"/works/OL45804W"'}).mock(
        return_value=Response(200, json=_load("ol_search_key_OL45804W.json"))
    )
    respx.get("https://openlibrary.org/works/OL45804W.json").mock(
        return_value=Response(200, json=_load("ol_work_OL45804W.json"))
    )


def _mock_book(external_id: str, index: int) -> None:
    respx.get("https://openlibrary.org/search.json", params={"q": f'key:"/works/{external_id}"'}).mock(
        return_value=Response(
            200, json={"docs": [{"key": f"/works/{external_id}", "title": f"Kitap {index}"}]}
        )
    )
    respx.get(f"https://openlibrary.org/works/{external_id}.json").mock(
        return_value=Response(200, json={"title": f"Kitap {index}", "description": "test"})
    )


@respx.mock
def test_rating_creates_log_activity(client, db, user_factory):
    _mock_book_detail()
    user = user_factory(username="puanlayan", email="puanlayan@example.com")
    client.put("/api/v1/library/book/OL45804W", json={"rating": 8}, headers=auth_headers(user))

    activity = db.query(Activity).filter_by(actor_id=user.id, verb="log").first()
    assert activity is not None


@respx.mock
def test_review_on_same_content_reuses_activity_and_sets_review_card_type(client, db, user_factory):
    _mock_book_detail()
    user = user_factory(username="incelemeciks", email="incelemeciks@example.com")
    headers = auth_headers(user)

    client.put("/api/v1/library/book/OL45804W", json={"rating": 9}, headers=headers)
    assert db.query(Activity).filter_by(actor_id=user.id, verb="log").count() == 1

    client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL45804W", "body": "Harika bir kitaptı, bayıldım."},
        headers=headers,
    )
    assert db.query(Activity).filter_by(actor_id=user.id, verb="log").count() == 1

    feed = client.get("/api/v1/feed", params={"scope": "global"})
    card = feed.json()["items"][0]
    assert card["card_type"] == "review"


@respx.mock
def test_review_is_edited_false_until_actually_updated(client, db, user_factory):
    # D-21: created_at/updated_at, TimestampMixin'de iki ayrı datetime.now(UTC) çağrısıyla
    # ayarlanıyor; bu yüzden is_edited hesaplaması saf `updated_at > created_at` yerine
    # gerçek bir düzenlemeyi ayırt edecek bir tolerans kullanmalı (bkz. app/modules/social/service.py).
    _mock_book_detail()
    user = user_factory(username="duzenleyen", email="duzenleyen@example.com")
    headers = auth_headers(user)

    create_resp = client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL45804W", "body": "İlk hâli, henüz düzenlenmedi."},
        headers=headers,
    )
    review_id = create_resp.json()["id"]

    reviews = client.get("/api/v1/reviews", params={"type": "book", "external_id": "OL45804W"})
    fresh = next(r for r in reviews.json()["items"] if r["id"] == review_id)
    assert fresh["is_edited"] is False

    review_row = db.get(Review, review_id)
    review_row.created_at = review_row.created_at - timedelta(minutes=5)
    db.commit()

    client.patch(f"/api/v1/reviews/{review_id}", json={"body": "Düzenlendi, artık farklı."}, headers=headers)

    reviews_after = client.get("/api/v1/reviews", params={"type": "book", "external_id": "OL45804W"})
    edited = next(r for r in reviews_after.json()["items"] if r["id"] == review_id)
    assert edited["is_edited"] is True


@respx.mock
def test_deleting_rating_and_review_removes_activity_with_likes_and_comments(client, db, user_factory):
    _mock_book_detail()
    user = user_factory(username="silinecekaktivite", email="silinecekaktivite@example.com")
    headers = auth_headers(user)
    liker = user_factory(username="begenen", email="begenen@example.com")

    client.put("/api/v1/library/book/OL45804W", json={"rating": 7}, headers=headers)
    review_resp = client.post(
        "/api/v1/reviews",
        json={"type": "book", "external_id": "OL45804W", "body": "Fena değildi, okunabilir."},
        headers=headers,
    )
    review_id = review_resp.json()["id"]

    activity_id = db.query(Activity).filter_by(actor_id=user.id, verb="log").first().id
    client.post(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(liker))
    client.post(
        f"/api/v1/activities/{activity_id}/comments",
        json={"body": "güzel yorum"},
        headers=auth_headers(liker),
    )

    client.put("/api/v1/library/book/OL45804W", json={"rating": None}, headers=headers)
    assert db.query(Activity).filter_by(id=activity_id).count() == 1

    client.delete(f"/api/v1/reviews/{review_id}", headers=headers)
    assert db.query(Activity).filter_by(id=activity_id).count() == 0
    assert db.query(ActivityLike).filter_by(activity_id=activity_id).count() == 0
    assert db.query(ActivityComment).filter_by(activity_id=activity_id).count() == 0


@respx.mock
def test_status_activity_reopens_within_60_minutes_then_creates_new_after(client, db, user_factory):
    _mock_book_detail()
    user = user_factory(username="durumdegisen", email="durumdegisen@example.com")
    headers = auth_headers(user)

    client.put("/api/v1/library/book/OL45804W", json={"status": "planned"}, headers=headers)
    assert db.query(Activity).filter_by(actor_id=user.id, verb="status").count() == 1

    client.put("/api/v1/library/book/OL45804W", json={"status": "in_progress"}, headers=headers)
    assert db.query(Activity).filter_by(actor_id=user.id, verb="status").count() == 1

    activity = db.query(Activity).filter_by(actor_id=user.id, verb="status").first()
    assert activity.status == "in_progress"

    activity.created_at = datetime.now(UTC) - timedelta(minutes=61)
    db.commit()

    client.put("/api/v1/library/book/OL45804W", json={"status": "completed"}, headers=headers)
    assert db.query(Activity).filter_by(actor_id=user.id, verb="status").count() == 2


@respx.mock
def test_feed_scope_following_includes_only_followed_and_self(client, db, user_factory):
    _mock_book_detail()
    me = user_factory(username="akisben", email="akisben@example.com")
    followed = user_factory(username="akistakipettigim", email="akistakipettigim@example.com")
    stranger = user_factory(username="akisyabanci", email="akisyabanci@example.com")

    client.post(f"/api/v1/users/{followed.username}/follow", headers=auth_headers(me))

    client.put("/api/v1/library/book/OL45804W", json={"rating": 6}, headers=auth_headers(me))
    client.put("/api/v1/library/book/OL45804W", json={"rating": 7}, headers=auth_headers(followed))
    client.put("/api/v1/library/book/OL45804W", json={"rating": 8}, headers=auth_headers(stranger))

    response = client.get("/api/v1/feed", params={"scope": "following"}, headers=auth_headers(me))
    actor_usernames = {item["actor"]["username"] for item in response.json()["items"]}
    assert actor_usernames == {"akisben", "akistakipettigim"}

    global_response = client.get("/api/v1/feed", params={"scope": "global"})
    global_usernames = {item["actor"]["username"] for item in global_response.json()["items"]}
    assert "akisyabanci" in global_usernames


@respx.mock
def test_feed_cursor_pagination(client, db, user_factory):
    user = user_factory(username="sayfalamatest", email="sayfalamatest@example.com")
    headers = auth_headers(user)

    for i in range(16):
        external_id = f"OL{1000 + i}W"
        _mock_book(external_id, i)
        response = client.put(f"/api/v1/library/book/{external_id}", json={"rating": 5}, headers=headers)
        assert response.status_code == 200

    first_page = client.get("/api/v1/feed", params={"scope": "global", "limit": 15})
    body = first_page.json()
    assert len(body["items"]) == 15
    assert body["next_cursor"] is not None

    second_page = client.get(
        "/api/v1/feed", params={"scope": "global", "limit": 15, "cursor": body["next_cursor"]}
    )
    assert len(second_page.json()["items"]) == 1


@respx.mock
def test_like_is_idempotent_and_notifies_once(client, db, user_factory):
    _mock_book_detail()
    owner = user_factory(username="aktivitesahibi", email="aktivitesahibi@example.com")
    liker = user_factory(username="begenenkisi", email="begenenkisi@example.com")

    client.put("/api/v1/library/book/OL45804W", json={"rating": 8}, headers=auth_headers(owner))
    activity_id = db.query(Activity).filter_by(actor_id=owner.id).first().id

    client.post(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(owner))
    assert db.query(Notification).filter_by(recipient_id=owner.id, type="like").count() == 0
    client.delete(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(owner))

    first = client.post(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(liker))
    second = client.post(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(liker))
    assert first.json()["likes_count"] == 1
    assert second.json()["likes_count"] == 1
    assert db.query(Notification).filter_by(recipient_id=owner.id, type="like").count() == 1

    client.delete(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(liker))
    client.post(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(liker))
    assert db.query(Notification).filter_by(recipient_id=owner.id, type="like").count() == 1


@respx.mock
def test_comment_permissions(client, db, user_factory):
    _mock_book_detail()
    owner = user_factory(username="yorumaktivite", email="yorumaktivite@example.com")
    commenter = user_factory(username="yorumyapan", email="yorumyapan@example.com")
    stranger = user_factory(username="yorumyabanci", email="yorumyabanci@example.com")

    client.put("/api/v1/library/book/OL45804W", json={"rating": 6}, headers=auth_headers(owner))
    activity_id = db.query(Activity).filter_by(actor_id=owner.id).first().id

    comment_resp = client.post(
        f"/api/v1/activities/{activity_id}/comments",
        json={"body": "ilk yorum"},
        headers=auth_headers(commenter),
    )
    comment_id = comment_resp.json()["id"]

    forbidden_edit = client.patch(
        f"/api/v1/comments/{comment_id}", json={"body": "değişti"}, headers=auth_headers(stranger)
    )
    assert forbidden_edit.status_code == 403

    forbidden_delete = client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers(stranger))
    assert forbidden_delete.status_code == 403

    owner_delete = client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers(owner))
    assert owner_delete.status_code == 204


@respx.mock
def test_feed_avoids_n_plus_one_queries(client, db, user_factory):
    author = user_factory(username="akisyazari", email="akisyazari@example.com")
    headers = auth_headers(author)

    for i in range(15):
        external_id = f"OL{2000 + i}W"
        _mock_book(external_id, i)
        response = client.put(f"/api/v1/library/book/{external_id}", json={"rating": 5}, headers=headers)
        assert response.status_code == 200

    query_count = 0

    def _count_queries(*_args, **_kwargs):
        nonlocal query_count
        query_count += 1

    event.listen(test_engine, "before_cursor_execute", _count_queries)
    try:
        response = client.get("/api/v1/feed", params={"scope": "global", "limit": 15})
        assert len(response.json()["items"]) == 15
    finally:
        event.remove(test_engine, "before_cursor_execute", _count_queries)

    assert query_count <= 12


def test_notifications_list_empty_for_new_user(client, user_factory):
    user = user_factory(username="bildirimsiz", email="bildirimsiz@example.com")
    response = client.get("/api/v1/notifications", headers=auth_headers(user))
    assert response.status_code == 200
    assert response.json() == {"items": [], "next_cursor": None}
    assert client.get("/api/v1/notifications/unread-count", headers=auth_headers(user)).json() == {"count": 0}


def test_follow_creates_notification_and_dedupes_while_unread(client, user_factory):
    followed = user_factory(username="takipedilennot", email="takipedilennot@example.com")
    follower = user_factory(username="takipedennot", email="takipedennot@example.com")

    client.post("/api/v1/users/takipedilennot/follow", headers=auth_headers(follower))
    items = client.get("/api/v1/notifications", headers=auth_headers(followed)).json()["items"]
    assert len(items) == 1
    assert items[0]["type"] == "follow"
    assert items[0]["actor"]["username"] == "takipedennot"
    assert items[0]["is_read"] is False

    # Takipten çık + tekrar takip et — bildirim hâlâ okunmadıysa ikinci bir bildirim eklenmiyor.
    client.delete("/api/v1/users/takipedilennot/follow", headers=auth_headers(follower))
    client.post("/api/v1/users/takipedilennot/follow", headers=auth_headers(follower))
    items = client.get("/api/v1/notifications", headers=auth_headers(followed)).json()["items"]
    assert len(items) == 1


@respx.mock
def test_like_and_comment_notifications_include_content_and_excerpt(client, db, user_factory):
    _mock_book_detail()
    owner = user_factory(username="bildirimsahibi", email="bildirimsahibi@example.com")
    other = user_factory(username="bildirimdigeri", email="bildirimdigeri@example.com")

    client.put("/api/v1/library/book/OL45804W", json={"rating": 7}, headers=auth_headers(owner))
    activity_id = db.query(Activity).filter_by(actor_id=owner.id).first().id

    client.post(f"/api/v1/activities/{activity_id}/like", headers=auth_headers(other))
    client.post(
        f"/api/v1/activities/{activity_id}/comments",
        json={"body": "harika bir kitap"},
        headers=auth_headers(other),
    )

    items = client.get("/api/v1/notifications", headers=auth_headers(owner)).json()["items"]
    assert len(items) == 2
    by_type = {item["type"]: item for item in items}
    assert by_type["like"]["content"]["title"] == "Fantastic Mr Fox"
    assert by_type["comment"]["comment_excerpt"] == "harika bir kitap"


def test_notifications_unread_count_and_mark_all_read(client, user_factory):
    followed = user_factory(username="okunmamisbildirim", email="okunmamisbildirim@example.com")
    for i in range(3):
        follower = user_factory(username=f"coktakipci{i}", email=f"coktakipci{i}@example.com")
        client.post("/api/v1/users/okunmamisbildirim/follow", headers=auth_headers(follower))

    headers = auth_headers(followed)
    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"count": 3}

    mark_all = client.post("/api/v1/notifications/read-all", headers=headers)
    assert mark_all.status_code == 204
    assert client.get("/api/v1/notifications/unread-count", headers=headers).json() == {"count": 0}
    items = client.get("/api/v1/notifications", headers=headers).json()["items"]
    assert all(item["is_read"] for item in items)


def test_mark_single_notification_read_requires_ownership(client, user_factory):
    followed = user_factory(username="tekbildirimsahibi", email="tekbildirimsahibi@example.com")
    follower = user_factory(username="tekbildirimtakip", email="tekbildirimtakip@example.com")
    stranger = user_factory(username="tekbildirimyabanci", email="tekbildirimyabanci@example.com")

    client.post("/api/v1/users/tekbildirimsahibi/follow", headers=auth_headers(follower))
    notification_id = client.get("/api/v1/notifications", headers=auth_headers(followed)).json()["items"][0][
        "id"
    ]

    forbidden = client.post(f"/api/v1/notifications/{notification_id}/read", headers=auth_headers(stranger))
    assert forbidden.status_code == 404

    ok = client.post(f"/api/v1/notifications/{notification_id}/read", headers=auth_headers(followed))
    assert ok.status_code == 204
    assert client.get("/api/v1/notifications/unread-count", headers=auth_headers(followed)).json() == {
        "count": 0
    }


def test_notifications_cursor_pagination(client, user_factory):
    followed = user_factory(username="sayfalibildirim", email="sayfalibildirim@example.com")
    for i in range(5):
        follower = user_factory(username=f"sayfatakipci{i}", email=f"sayfatakipci{i}@example.com")
        client.post("/api/v1/users/sayfalibildirim/follow", headers=auth_headers(follower))

    headers = auth_headers(followed)
    first_page = client.get("/api/v1/notifications", params={"limit": 3}, headers=headers).json()
    assert len(first_page["items"]) == 3
    assert first_page["next_cursor"] is not None

    second_page = client.get(
        "/api/v1/notifications", params={"limit": 3, "cursor": first_page["next_cursor"]}, headers=headers
    ).json()
    assert len(second_page["items"]) == 2
    assert second_page["next_cursor"] is None
