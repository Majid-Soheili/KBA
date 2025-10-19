from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable
from sqlmodel import SQLModel, Field, Session, create_engine, select, delete

from src.model.Article import Article
from src.model.ArticleType import ArticleType
from src.model.Feature import Feature
from src.model.Subject import Subject
from src.repository.DBConnection import DBConnection
from sqlalchemy import inspect

class DBInit:
    def __init__(self, connection: DBConnection):
        self.engine = connection.engine

    def initialize(self, override:bool = False):
        if override:
            self.drop_tables()
            self.create_tables()
            self.seed_data()
            return

        if not inspect(self.engine).has_table('article'):
            self.create_tables()
            self.seed_data()

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def drop_tables(self):
        SQLModel.metadata.drop_all(self.engine)

    def clear_data(self):
        with Session(self.engine) as session:
            session.exec(delete(Feature))
            session.exec(delete(Subject))
            session.exec(delete(Article))
            session.exec(delete(ArticleType))
            session.commit()

    def seed_data(self):
        self.seed_subjects()
        self.seed_features()
        self.seed_types()

    def _seed_entities(self, entities, entity_class):
        with Session(self.engine) as session:
            for entity in entities:
                session.add(entity)
            session.commit()

    def seed_subjects(self):
        subjects = [
            Subject(subject_id=0, name="Getting Started", description="Description for Subject A"),
            Subject(subject_id=1, name="Configuration", description="Description for Subject B"),
            Subject(subject_id=2, name="Main Functionality", description="Description for Subject C"),
            Subject(subject_id=3, name="AI Assistant", description="Description for Subject D"),
            Subject(subject_id=4, name="Chat", description="Description for Subject E"),
            Subject(subject_id=5, name="Using the Q&A", description="Description for Subject F"),
            Subject(subject_id=6, name="Redaction", description="Description for Subject G")]
        self._seed_entities(subjects, Subject)

    def seed_features(self):
        features = [
            Feature(feature_id=1, subject_id=1, name="User Account Setup", description=""),
            Feature(feature_id=2, subject_id=1, name="Personal Notifications Settings", description=""),
            Feature(feature_id=3, subject_id=2, name="Navigating Projects", description=""),
            Feature(feature_id=4, subject_id=2, name="Index Features", description=""),
            Feature(feature_id=5, subject_id=2, name="Searching and Filtering", description=""),
            Feature(feature_id=6, subject_id=3, name="Using AI", description=""),
            Feature(feature_id=7, subject_id=5, name="Q&A Introduction", description=""),
            Feature(feature_id=8, subject_id=5, name="Question Role", description=""),
            Feature(feature_id=9, subject_id=5, name="Selection Role", description=""),
            Feature(feature_id=10, subject_id=5, name="Distribution Role", description=""),
            Feature(feature_id=11,subject_id=5,  name="Answer Role", description=""),
            Feature(feature_id=12,subject_id=5,  name="Approval Role", description=""),
            Feature(feature_id=13,subject_id=5,  name="Visitor Role", description=""),
            Feature(feature_id=14,subject_id=6,  name="Redacting Documents", description=""),
            Feature(feature_id=15,subject_id=6,  name="Redacting Search Terms", description=""),
            Feature(feature_id=16,subject_id=6,  name="Redacting Terms Matching Sensitive Data Categories", description=""),
            Feature(feature_id=17,subject_id=6,  name="Redacting Selected Document Areas", description=""),
            Feature(feature_id=18,subject_id=6,  name="Batch Redacting Documents", description="")]
        self._seed_entities(features, Feature)

    def seed_types(self):
        types = [
            ArticleType(type_id=3, feature_id=1),
            ArticleType(type_id=3, feature_id=2),
            ArticleType(type_id=3, feature_id=3),
            ArticleType(type_id=3, feature_id=4),
            ArticleType(type_id=1, feature_id=5),
            ArticleType(type_id=3, feature_id=5),
            ArticleType(type_id=1, feature_id=6),
            ArticleType(type_id=3, feature_id=6),
            ArticleType(type_id=3, feature_id=7),
            ArticleType(type_id=3, feature_id=8),
            ArticleType(type_id=3, feature_id=9),
            ArticleType(type_id=3, feature_id=10),
            ArticleType(type_id=3, feature_id=11),
            ArticleType(type_id=3, feature_id=12),
            ArticleType(type_id=3, feature_id=13),
            ArticleType(type_id=3, feature_id=14),
            ArticleType(type_id=3, feature_id=15),
            ArticleType(type_id=3, feature_id=16),
            ArticleType(type_id=3, feature_id=17),
            ArticleType(type_id=3, feature_id=18),
            ]
        self._seed_entities(types, ArticleType)