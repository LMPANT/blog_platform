import uuid

from slugify import slugify as _slugify
from sqlalchemy.orm import Session


def unique_slug(db: Session, model, text: str, field: str = "slug") -> str:
    """Generate a URL-friendly slug and append a short suffix if it collides."""
    base = _slugify(text)
    candidate = base
    query = db.query(model).filter(getattr(model, field) == candidate)
    if query.first() is None:
        return candidate
    return f"{base}-{uuid.uuid4().hex[:6]}"
