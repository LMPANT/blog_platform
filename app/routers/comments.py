from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.comment import CommentCreate, CommentOut
from app.crud import comment as comment_crud
from app.crud import post as post_crud
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.get("/", response_model=List[CommentOut])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    if not post_crud.get_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return comment_crud.get_comments_for_post(db, post_id)


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not post_crud.get_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return comment_crud.create_comment(db, comment_in, post_id=post_id, author_id=current_user.id)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = comment_crud.get_comment(db, comment_id)
    if not comment or comment.post_id != post_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    comment_crud.delete_comment(db, comment)
