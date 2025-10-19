from sqlmodel import select
from src.model.Feature import Feature
from src.model.Subject import Subject
from src.model.Article import Article
from typing import List
from collections import defaultdict
from sqlalchemy.orm import selectinload
import json

class ArticleRepository:
    def __init__(self, session):
        self.session = session

    def get_article(self, feature_name:str, article_type:int) -> Article:
        return self.session.exec(
            select(Article)
            .join(Feature, Feature.feature_id == Article.feature_id)
            .where(Feature.name == feature_name)
            .where(Article.type_id == article_type)
            .order_by(Article.article_id)
        ).first()

    def get_articles(self, feature_name:str) -> List[Article]:
        return self.session.exec(
            select(Article)
            .join(Feature, Feature.feature_id == Article.feature_id)
            .where(Feature.name == feature_name)
            .order_by(Article.article_id)
        ).all()


