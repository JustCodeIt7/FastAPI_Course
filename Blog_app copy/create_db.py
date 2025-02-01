# create_db.py
from sqlmodel import SQLModel
from main import engine

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
