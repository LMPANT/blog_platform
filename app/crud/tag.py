from typing import List
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.utils.slugify import unique_slug


def get_tags(db: Session) -> List[Tag]:
    return db.query(Tag).order_by(Tag.name).all()


def get_or_create_tags(db: Session, names: List[str]) -> List[Tag]:
    """Look up tags by (case-insensitive) name, creating any that don't exist yet.

    Dedupes input names (case-insensitively) so passing e.g. ["FastAPI", "fastapi"]
    doesn't attempt to attach the same tag twice.
    """
    seen_ids = set()
    tags = []
    for raw_name in names:
        name = raw_name.strip()
        if not name:
            continue
        tag = db.query(Tag).filter(Tag.name.ilike(name)).first()
        if not tag:
            tag = Tag(name=name, slug=unique_slug(db, Tag, name))
            db.add(tag)
            db.flush()  # get an id without committing yet
        if tag.id not in seen_ids:
            seen_ids.add(tag.id)
            tags.append(tag)
    return tags
