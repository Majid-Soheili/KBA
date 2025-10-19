import os
from pathlib import Path
from sqlmodel import create_engine

class DBConnection:

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name = 'documents.db', echo: bool = False):
        db_dir = os.getenv("DB_PATH", ".")
        db_path = Path(db_dir) / db_name
        db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(db_url, echo=echo)

    def get_engine(self):
        return self.engine
