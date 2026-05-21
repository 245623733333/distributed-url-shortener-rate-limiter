import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ShortLink

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(number: int) -> str:
    if number == 0:
        return ALPHABET[0]
    result = []
    while number:
        number, remainder = divmod(number, 62)
        result.append(ALPHABET[remainder])
    return "".join(reversed(result))


def is_expired(link: ShortLink) -> bool:
    if not link.expires_at:
        return False
    expires_at = link.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= datetime.now(timezone.utc)


def generate_unique_code(db: Session, seed: int) -> str:
    candidate = base62_encode(seed)
    exists = db.scalar(select(ShortLink).where(ShortLink.code == candidate))
    if not exists:
        return candidate

    # Collision fallback for custom imports, sequence resets, or cross-region writes.
    for _ in range(8):
        candidate = f"{base62_encode(seed)}{secrets.token_urlsafe(3).replace('-', '').replace('_', '')[:4]}"
        exists = db.scalar(select(ShortLink).where(ShortLink.code == candidate))
        if not exists:
            return candidate
    raise RuntimeError("Could not generate unique short code.")
