# %%
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Session, SQLModel, create_engine, select
from rich import print


# %%
# Define the database URL
DATABASE_URL = "sqlite:///tutorial.db"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)


# %%
# Define the models
class Hero(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

# %%
print("################## Resetting database and tables ##################")
# Drop and create the database and tables
def reset_db_and_tables():
    SQLModel.metadata.drop_all(engine)  # Drop all tables if they exist
    SQLModel.metadata.create_all(engine)  # Create tables

reset_db_and_tables()



# %%
print("\n################## Adding heroes to the database ############\n")
# Add a hero to the database
def create_hero(name: str, secret_name: str, age: Optional[int] = None):
    with Session(engine) as session:
        hero = Hero(name=name, secret_name=secret_name, age=age)
        session.add(hero)
        session.commit()
        session.refresh(hero)
        print(f"Created hero: {hero}")

create_hero(name="Deadpond", secret_name="Dive Wilson", age=30)
create_hero(name="Spider-Boy", secret_name="Pedro Parqueador", age=18)
create_hero(name="Iron Man", secret_name="The Goat", age=48)


# %%
print("\n############ Getting all heroes from the database ##########\n")

def get_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        print("Heroes in the database:")
        for hero in heroes:
            print(hero)
            
# %%
# Get all heroes
get_heroes()


# %%
print("\n################## Updating a hero's age ##################\n")
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

# %%
# Update a hero's age
hero_id_to_update = '9fa95e46-a8a9-4f2f-a31a-ad5750ba7138'
new_age = 50
update_hero_age(UUID(hero_id_to_update), new_age)

# Get all heroes again
get_heroes()
# %%
print("\n################## Deleting a hero ##################\n")
def delete_hero(hero_id: UUID):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            print("Hero not found!")
            return
        session.delete(hero)
        session.commit()
        print(f"Deleted hero with ID: {hero_id}")

# %%
# Delete a hero
hero_id_to_delete = "8a348c64-d239-4574-b8f6-19a754aac00d"
delete_hero(UUID(hero_id_to_delete))

# Get all heroes again
get_heroes()
