import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuthorSchema(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: uuid.UUID
    content: Optional[str]
    image_url: Optional[str]
    visibility: str
    like_count: int
    comment_count: int
    created_at: datetime
    author: AuthorSchema
    liked_by_me: bool

    class Config:
        from_attributes = True


class PostCreateRequest(BaseModel):
    content: Optional[str] = None
    visibility: str = "public"


class PostUpdateRequest(BaseModel):
    content: Optional[str] = None
    visibility: Optional[str] = None
