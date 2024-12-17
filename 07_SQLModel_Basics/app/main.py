from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Hero(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine, checkfirst=True)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: Create the database and tables
    create_db_and_tables()
    yield
    # Shutdown event: Add any cleanup logic here if needed


app = FastAPI()


@app.post("/heroes/")
def create_hero(hero: Hero):
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/")
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application with reload enabled
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
