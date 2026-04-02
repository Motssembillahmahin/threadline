import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )
    content: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None, max_length=500)
    visibility: str = Field(default="public", max_length=10, nullable=False)
    like_count: int = Field(default=0, nullable=False)
    comment_count: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
