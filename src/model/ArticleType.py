from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from datetime import timezone
from typing import Optional, List

# type 1 = 'FAQ'
# type 2 = 'Troubleshooting'
# type 3 = 'Tutorials'
class ArticleType(SQLModel, table=True):
    __tablename__ = "article_type"
    type_id: int = Field(primary_key=True)
    feature_id: int = Field(primary_key=True, foreign_key="feature.feature_id")
    updated_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})

    features: List["Feature"] = Relationship(back_populates="article_types")
    def __repr__(self):
        return f"<ArticleType(type_id={self.type_id})>"