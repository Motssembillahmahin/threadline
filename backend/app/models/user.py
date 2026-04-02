import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    first_name: str = Field(max_length=100, nullable=False)
    last_name: str = Field(max_length=100, nullable=False)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
