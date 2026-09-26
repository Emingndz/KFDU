import io
import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.errors import AppError

MAX_AVATAR_BYTES = 2 * 1024 * 1024
AVATAR_SIZE = 256
ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})


def save_avatar(user_id: int, content_type: str, data: bytes) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise AppError(422, "INVALID_IMAGE", "Yalnızca JPG, PNG veya WEBP yükleyebilirsin")
    if len(data) > MAX_AVATAR_BYTES:
        raise AppError(422, "IMAGE_TOO_LARGE", "Görsel en fazla 2 MB olabilir")

    try:
        Image.open(io.BytesIO(data)).verify()
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise AppError(422, "INVALID_IMAGE", "Görsel dosyası bozuk veya okunamıyor") from exc

    side = min(image.width, image.height)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    cropped = image.crop((left, top, left + side, top + side)).resize((AVATAR_SIZE, AVATAR_SIZE))

    avatars_dir = Path(settings.MEDIA_DIR) / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.webp"
    cropped.save(avatars_dir / filename, "WEBP", quality=85)

    return f"/media/avatars/{filename}"


def delete_avatar_file(avatar_url: str) -> None:
    filename = avatar_url.rsplit("/", 1)[-1]
    path = Path(settings.MEDIA_DIR) / "avatars" / filename
    path.unlink(missing_ok=True)
