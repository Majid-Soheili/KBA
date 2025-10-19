from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from datetime import timezone
from typing import Optional, List
from src.model.ArticleType import ArticleType
from src.model.Subject import Subject

class Feature(SQLModel, table=True):
    feature_id: int = Field(primary_key=True)
    subject_id: int = Field(foreign_key="subject.subject_id")
    name: str = Field(nullable=False)
    updated_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})

    subject: Subject = Relationship(back_populates="features")
    article_types: List[ArticleType] = Relationship(back_populates="features")

    def __repr__(self):
        return f"<Feature(id={self.feature_id}, name={self.name})>"

    def __str__(self):
        return self.__repr__()