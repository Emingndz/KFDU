import io

from PIL import Image

from app.core.config import settings
from app.modules.catalog.models import Content
from app.modules.library.models import LibraryEntry, Review


def _register(client, username: str, email: str, password: str = "Sifre1234") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "password_confirm": password,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_profile_does_not_expose_email(client):
    _register(client, "profilkullanici", "profil@example.com")
    response = client.get("/api/v1/users/profilkullanici")
    assert response.status_code == 200
    assert "email" not in response.json()


def test_search_requires_auth_and_hides_email(client):
    _register(client, "aramakullanici", "arama@example.com")

    anon = client.get("/api/v1/users/search", params={"q": "arama"})
    assert anon.status_code == 401

    body = _register(client, "aramakullanici2", "arama2@example.com")
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    response = client.get("/api/v1/users/search", params={"q": "arama"}, headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    assert all("email" not in item for item in items)


def test_follow_and_unfollow_are_idempotent(client):
    a = _register(client, "takipeden", "takipeden@example.com")
    _register(client, "takipedilen", "takipedilen@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}

    first = client.post("/api/v1/users/takipedilen/follow", headers=headers)
    second = client.post("/api/v1/users/takipedilen/follow", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == {"following": True, "followers_count": 1}
    assert second.json() == {"following": True, "followers_count": 1}

    first_unfollow = client.delete("/api/v1/users/takipedilen/follow", headers=headers)
    second_unfollow = client.delete("/api/v1/users/takipedilen/follow", headers=headers)
    assert first_unfollow.json() == {"following": False, "followers_count": 0}
    assert second_unfollow.json() == {"following": False, "followers_count": 0}


def test_follow_self_returns_400(client):
    a = _register(client, "kendinitakip", "kendini@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}
    response = client.post("/api/v1/users/kendinitakip/follow", headers=headers)
    assert response.status_code == 400
    assert response.json()["code"] == "CANNOT_FOLLOW_SELF"


def test_update_username_conflict_returns_409(client):
    a = _register(client, "kullaniciA", "a@example.com")
    _register(client, "kullaniciB", "b@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}

    response = client.patch("/api/v1/users/me", json={"username": "kullaniciB"}, headers=headers)
    assert response.status_code == 409
    assert response.json()["code"] == "USERNAME_TAKEN"


def test_change_email_wrong_password_returns_400(client):
    a = _register(client, "epostadegis", "eposta@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}

    response = client.put(
        "/api/v1/users/me/email",
        json={"new_email": "yeni@example.com", "current_password": "YanlisSifre1"},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PASSWORD"


def test_avatar_upload_converts_to_webp(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    a = _register(client, "avatarli", "avatar@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}

    image = Image.new("RGB", (400, 300), color=(255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    response = client.post(
        "/api/v1/users/me/avatar",
        headers=headers,
        files={"file": ("avatar.png", buffer.getvalue(), "image/png")},
    )
    assert response.status_code == 200
    avatar_url = response.json()["avatar_url"]
    assert avatar_url.endswith(".webp")

    saved_path = tmp_path / "avatars" / avatar_url.rsplit("/", 1)[-1]
    assert saved_path.exists()
    with Image.open(saved_path) as saved:
        assert saved.format == "WEBP"
        assert saved.size == (256, 256)


def test_avatar_upload_corrupt_image_returns_422(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MEDIA_DIR", str(tmp_path))
    a = _register(client, "avatarbozuk", "avatarbozuk@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}

    image = Image.new("RGB", (10, 10), color=(0, 255, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    data = bytearray(buffer.getvalue())
    data[len(data) // 2] ^= 0xFF  # IDAT/CRC'yi boz — Pillow SyntaxError fırlatır

    response = client.post(
        "/api/v1/users/me/avatar",
        headers=headers,
        files={"file": ("avatar.png", bytes(data), "image/png")},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_IMAGE"


def test_delete_account_cascades_entries_and_reviews(client, db):
    a = _register(client, "silinecek", "silinecek@example.com")
    headers = {"Authorization": f"Bearer {a['access_token']}"}
    user_id = a["user"]["id"]

    content = Content(type="movie", source="tmdb", external_id="silinecek-1", title="Test Film")
    db.add(content)
    db.commit()
    db.add(LibraryEntry(user_id=user_id, content_id=content.id, status="completed"))
    db.add(Review(user_id=user_id, content_id=content.id, body="Güzel bir filmdi, tavsiye ederim."))
    db.commit()

    response = client.request("DELETE", "/api/v1/users/me", json={"password": "Sifre1234"}, headers=headers)
    assert response.status_code == 204

    assert db.query(LibraryEntry).filter_by(user_id=user_id).count() == 0
    assert db.query(Review).filter_by(user_id=user_id).count() == 0
