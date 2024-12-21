from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from uuid import UUID, uuid4

# Define the database URL
DATABASE_URL = "sqlite:///tutorial.db"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)


# Define the models
class Hero(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Add a hero to the database
def create_hero(name: str, secret_name: str, age: Optional[int] = None):
    with Session(engine) as session:
        hero = Hero(name=name, secret_name=secret_name, age=age)
        session.add(hero)
        session.commit()
        session.refresh(hero)
        print(f"Created hero: {hero}")


# Get all heroes from the database
def get_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        print("Heroes in the database:")
        for hero in heroes:
            print(hero)


# Update a hero's age
def update_hero_age(hero_id: UUID, new_age: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            print("Hero not found!")
            return
        hero.age = new_age
        session.add(hero)
        session.commit()
        session.refresh(hero)
        print(f"Updated hero: {hero}")


# Delete a hero
def delete_hero(hero_id: UUID):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            print("Hero not found!")
            return
        session.delete(hero)
        session.commit()
        print(f"Deleted hero with ID: {hero_id}")


# Main function to demonstrate SQLModel features
if __name__ == "__main__":
    # Create the database and tables
    create_db_and_tables()

    # Create some heroes
    create_hero(name="Deadpond", secret_name="Dive Wilson", age=30)
    create_hero(name="Spider-Boy", secret_name="Pedro Parqueador", age=18)
    create_hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    # Get all heroes
    get_heroes()

    # Update a hero's age
    hero_id_to_update = input("Enter the ID of the hero to update: ")
    new_age = int(input("Enter the new age: "))
    update_hero_age(UUID(hero_id_to_update), new_age)

    # Get all heroes again
    get_heroes()

    # Delete a hero
    hero_id_to_delete = input("Enter the ID of the hero to delete: ")
    delete_hero(UUID(hero_id_to_delete))

    # Get all heroes again
    get_heroes()
