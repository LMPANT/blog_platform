from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.post import PostCreate, PostUpdate, PostListOut, PostDetailOut
from app.crud import post as post_crud
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.post import Post

router = APIRouter(prefix="/posts", tags=["posts"])


def _get_owned_post_or_404(db: Session, post_id: int, current_user: User) -> Post:
    post = post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return post


@router.get("/", response_model=List[PostListOut])
def list_posts(
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    category_id: Optional[int] = None,
    tag: Optional[str] = Query(default=None, description="Filter by tag slug"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return post_crud.get_posts(
        db, skip=skip, limit=limit, category_id=category_id, tag_slug=tag, search=search
    )


@router.get("/{slug}", response_model=PostDetailOut)
def read_post(slug: str, db: Session = Depends(get_db)):
    post = post_crud.get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post_crud.increment_view_count(db, post)
    return post


@router.post("/", response_model=PostDetailOut, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return post_crud.create_post(db, post_in, author_id=current_user.id)


@router.patch("/{post_id}", response_model=PostDetailOut)
def update_post(
    post_id: int,
    post_in: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = _get_owned_post_or_404(db, post_id, current_user)
    return post_crud.update_post(db, post, post_in)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = _get_owned_post_or_404(db, post_id, current_user)
    post_crud.delete_post(db, post)
