from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.tag import TagOut
from app.crud import tag as tag_crud

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagOut])
def list_tags(db: Session = Depends(get_db)):
    """Tags are created automatically when used on a post (via tag_names)."""
    return tag_crud.get_tags(db)
