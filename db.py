from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


def get_session():
    return SessionLocal()