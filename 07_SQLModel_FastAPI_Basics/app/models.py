from typing import Optional
from sqlmodel import Field, SQLModel


# Base model for Hero
class HeroBase(SQLModel):
    name: str
    secret_name: str
    age: Optional[int] = None


# Table model
class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Request model for creating a hero
class HeroCreate(HeroBase):
    pass


# Response model for returning heroes
class HeroRead(HeroBase):
    id: int
