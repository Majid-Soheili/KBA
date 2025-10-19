from sqlmodel import Session, select
from datetime import datetime, timezone
from src.model.Subject import Subject


class SubjectRepository:
    def __init__(self, session: Session):
        self.session = session
    def list_all(self) -> list[Subject]:
        return list(self.session.exec(select(Subject)))

    def get_names(self) -> str:
        rows = self.session.exec(select(Subject.name)).all()  # list of 1-tuples
        names = ", ".join(r if isinstance(r, str) else r[0] for r in rows)
        return names