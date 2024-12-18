# %%
from sqlmodel import SQLModel, Field

# %%


class User(SQLModel, table=True):
    username: str = Field(primary_key=True)
    email: str
    full_name: str
    bio: str = None
    hashed_password: str
    is_active: bool = True


# %%

# Integrating Alembic for Database Migrations

# %%
