# database.py
from sqlmodel import create_engine, Session, SQLModel
import os

# Delete the existing database file if it exists
DATABASE_PATH = "../../../blog.db"
if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
