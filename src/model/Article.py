from datetime import datetime
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import timezone

class Article(SQLModel, table=True):
    article_id: int | None = Field(default=None, primary_key=True) # AutoIncremental Id
    feature_id: int = Field(foreign_key="feature.feature_id")
    type_id: int = Field(foreign_key="article_type.type_id")
    version: int = Field(default=0)
    hash_file_document:str = Field(default="")
    hash_file_article:str = Field(default="")
    last_update: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    def __repr__(self):
        return (
            f"<Document(subject_id={self.subject_id}, "
            f"feature_id={self.feature_id}, type_id={self.type_id}, "
            f"version={self.version})>"
        )