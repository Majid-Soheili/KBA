from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from datetime import timezone
from typing import Optional, List

class Subject(SQLModel, table=True):
    subject_id: int = Field(primary_key=True)
    name: str
    description: str | None = None
    updated_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})
    features : List["Feature"] = Relationship(back_populates="subject", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    def __repr__(self):
        return f"<Subject(id={self.subject_id}, name={self.name})>"