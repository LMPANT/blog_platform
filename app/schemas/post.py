import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut
from app.schemas.category import CategoryOut
from app.schemas.comment import CommentOut
from app.schemas.tag import TagOut


class PostBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = None
    is_published: bool = True


class PostCreate(PostBase):
    category_id: Optional[int] = None
    tag_names: List[str] = Field(default_factory=list, description="Tag names; created if they don't exist")


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
    tag_names: Optional[List[str]] = None


class PostOut(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    view_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: UserOut
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []


class PostListOut(BaseModel):
    """Lighter-weight shape for list views (no full content)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    cover_image_url: Optional[str] = None
    view_count: int
    created_at: datetime.datetime
    author: UserOut
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []


class PostDetailOut(PostOut):
    comments: List[CommentOut] = []
