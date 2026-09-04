import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    pass


class CommentOut(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    created_at: datetime.datetime
    author: UserOut
