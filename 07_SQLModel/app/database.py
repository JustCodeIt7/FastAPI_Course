# database.py
from sqlmodel import create_engine, Session, SQLModel
import os

# Delete the existing database file if it exists
DATABASE_PATH = "../../blog.db"

if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """
    Initialize the database by creating all tables defined within the SQLModel metadata.

    This function interacts with the database engine to ensure all the tables specified
    in the metadata of SQLModel are created and ready for use. It is generally called
    at the setup phase of an application to prepare the database schema.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Provides a generator function for creating a session with the database engine
    and ensures proper cleanup of resources. This is typically used for managing
    database connections within a context manager.

    Yields:
        SQLAlchemy session within a transactional scope. Ensures that the
        database session is properly closed after its usage.
    """
    with Session(engine) as session:
        yield session
