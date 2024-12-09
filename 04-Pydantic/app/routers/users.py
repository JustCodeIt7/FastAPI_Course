# app/routers/users.py

from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas import User, UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=User)
async def post_user(user: User):
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Username 'admin' is reserved")
    return user


@router.post("/create/", response_model=UserResponse)
async def post_user_with_password(user: UserCreate):
    # Here you would typically hash the password and save the user to the database
    new_user = UserResponse(id=1, username=user.username, email=user.email)
    return new_user


@router.get("/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    if username == "not_found":
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=1, username=username, email=f"{username}@example.com")


@router.get("/", response_model=List[UserResponse])
async def get_users_list(skip: int = 0, limit: int = 10):
    users = [
        UserResponse(id=i, username=f"user{i}", email=f"user{i}@example.com")
        for i in range(skip, skip + limit)
    ]
    return users
