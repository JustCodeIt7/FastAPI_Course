# Project Structure

``` markdown
blog_app/
├── main.py
├── models.py
├── database.py
├── schemas.py
```

1. **Model Association**:
    - Relationships establish how one model (`table`) is related to another. For example:
        - A `User` can have multiple `Post` objects (`One-to-Many` relationship).
        - A `Post` can have multiple `Comment` objects (`One-to-Many` relationship).
        - A `Comment` is associated with one `User` and one `Post` (`Many-to-One` relationship).

2. **Setting up Relationships**:
    - Relationships are declared using the `Relationship` function from `sqlmodel`.
    - They use the `back_populates` parameter to establish two-way connections between models.

3. **Foreign Keys**:
    - Foreign keys explicitly store the reference in the database to the related record.
    - For example, in the `Post` model, the `author_id` field is a foreign key (`Field(foreign_key="user.id")`) linking
      a specific post to a user