from sqlmodel import select
from src.model.Feature import Feature
from src.model.Subject import Subject
from collections import defaultdict
from sqlalchemy.orm import selectinload
import json

class FeatureRepository:
    def __init__(self, session):
        self.session = session

    def get_names(self) -> str:
        rows = self.session.exec(
            select(Subject.name, Feature.name)
            .join(Subject, Feature.subject_id == Subject.subject_id)
            .order_by(Subject.name, Feature.name)
        ).all()

        grouped: dict[str, list[str]] = defaultdict(list)
        for subject_name, feature_name in rows:
            grouped[subject_name].append(feature_name)

        lines = []
        for subject_name, features in grouped.items():
            lines.append(f"subject: {subject_name}")
            for f_name in features:
                lines.append(f"   feature: {f_name}")

        return "\n".join(lines)

    def find_by_name(self, feature_name: str, subject_name: str) -> Feature:
        statement = (
            select(Feature)
            .options(selectinload(Feature.article_types))
            .join(Subject, Feature.subject_id == Subject.subject_id)
            .where(Subject.name == subject_name)
            .where(Feature.name == feature_name)
        )
        return self.session.exec(statement).first()

    def find_by_json(self, payload: str) -> Feature:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON payload: {e}") from e

        subject_name = data.get("subject")
        if subject_name is None:
            raise ValueError(f"Invalid JSON payload: {payload}")
        feature_name = data.get("feature")
        if feature_name is None:
            raise ValueError(f"Invalid JSON payload: {payload}")

        return self.find_by_name(feature_name, subject_name)