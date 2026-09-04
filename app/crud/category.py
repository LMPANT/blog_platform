from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate
from app.utils.slugify import unique_slug


def get_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.name).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    category = Category(
        name=category_in.name,
        description=category_in.description,
        slug=unique_slug(db, Category, category_in.name),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
