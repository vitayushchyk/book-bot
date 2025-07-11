from datetime import datetime

from sqlmodel import Field, SQLModel


class UserComment(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    username: str | None = Field(default=None, max_length=64, nullable=False)
    comment: str = Field(max_length=1000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
