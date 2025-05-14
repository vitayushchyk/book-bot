from datetime import datetime

from sqlmodel import Field, SQLModel


class BookDB(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    title: str = Field(max_length=500, nullable=False)
    price: float = Field(nullable=False)
    url: str = Field(max_length=500, nullable=False)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
