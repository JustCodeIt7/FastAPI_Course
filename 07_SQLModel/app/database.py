# database.py
from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///../../../blog.db"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
