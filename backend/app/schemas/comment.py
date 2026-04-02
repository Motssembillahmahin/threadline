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


class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    like_count: int
    reply_count: int
    created_at: datetime
    author: AuthorSchema
    liked_by_me: bool

    class Config:
        from_attributes = True


class ReplyResponse(BaseModel):
    id: uuid.UUID
    content: str
    like_count: int
    created_at: datetime
    author: AuthorSchema
    liked_by_me: bool

    class Config:
        from_attributes = True


class CommentCreateRequest(BaseModel):
    content: str


class ReplyCreateRequest(BaseModel):
    content: str


class LikedUserSchema(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    avatar_url: Optional[str]

    class Config:
        from_attributes = True
