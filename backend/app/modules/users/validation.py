import re

USERNAME_PATTERN = re.compile(r"^[a-z][a-z0-9_.]{2,29}$")

RESERVED_USERNAMES = frozenset(
    {
        "admin",
        "api",
        "kfdu",
        "ayarlar",
        "kesfet",
        "giris",
        "kayit",
        "u",
        "liste",
        "film",
        "dizi",
        "kitap",
        "asistan",
        "oneriler",
        "bildirimler",
    }
)


def validate_username(value: str) -> str:
    value = value.lower()
    if not USERNAME_PATTERN.match(value):
        raise ValueError(
            "Kullanıcı adı küçük harfle başlamalı; yalnızca küçük harf, rakam, '_' ve '.' içerebilir "
            "(3-30 karakter)"
        )
    if value in RESERVED_USERNAMES:
        raise ValueError("Bu kullanıcı adı kullanılamaz")
    return value
