import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel


class PostLike(SQLModel, table=True):
    __tablename__ = "post_likes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CommentLike(SQLModel, table=True):
    __tablename__ = "comment_likes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    comment_id: uuid.UUID = Field(foreign_key="comments.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ReplyLike(SQLModel, table=True):
    __tablename__ = "reply_likes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reply_id: uuid.UUID = Field(foreign_key="replies.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
