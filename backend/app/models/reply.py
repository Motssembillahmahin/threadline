import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel


class Reply(SQLModel, table=True):
    __tablename__ = "replies"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    comment_id: uuid.UUID = Field(foreign_key="comments.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    content: str = Field(nullable=False)
    like_count: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
