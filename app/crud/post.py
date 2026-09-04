from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.post import Post
from app.models.tag import Tag
from app.schemas.post import PostCreate, PostUpdate
from app.utils.slugify import unique_slug
from app.crud.tag import get_or_create_tags


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    tag_slug: Optional[str] = None,
    search: Optional[str] = None,
    published_only: bool = True,
) -> List[Post]:
    query = db.query(Post)
    if published_only:
        query = query.filter(Post.is_published.is_(True))
    if category_id:
        query = query.filter(Post.category_id == category_id)
    if tag_slug:
        query = query.join(Post.tags).filter(Tag.slug == tag_slug)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Post.title.ilike(like), Post.content.ilike(like)))
    return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()


def get_post_by_slug(db: Session, slug: str) -> Optional[Post]:
    return db.query(Post).filter(Post.slug == slug).first()


def create_post(db: Session, post_in: PostCreate, author_id: int) -> Post:
    post = Post(
        title=post_in.title,
        content=post_in.content,
        summary=post_in.summary,
        cover_image_url=post_in.cover_image_url,
        is_published=post_in.is_published,
        category_id=post_in.category_id,
        author_id=author_id,
        slug=unique_slug(db, Post, post_in.title),
    )
    if post_in.tag_names:
        post.tags = get_or_create_tags(db, post_in.tag_names)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post, post_in: PostUpdate) -> Post:
    data = post_in.model_dump(exclude_unset=True, exclude={"tag_names"})
    for field, value in data.items():
        setattr(post, field, value)
    if post_in.tag_names is not None:
        post.tags = get_or_create_tags(db, post_in.tag_names)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()


def increment_view_count(db: Session, post: Post) -> Post:
    post.view_count += 1
    db.commit()
    db.refresh(post)
    return post
