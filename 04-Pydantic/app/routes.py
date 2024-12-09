from fastapi import APIRouter, HTTPException
from models import User, Order, UserCreate, UserResponse
from typing import List

router = APIRouter()


@router.get("/")
async def get_root():
    return {"message": "Hello FastAPI!"}


@router.post("/users/", response_model=User)
async def post_user(user: User):
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Username 'admin' is reserved")
    return user


@router.post("/orders/", response_model=Order)
async def post_order(order: Order):
    return order


@router.post("/users/create/", response_model=UserResponse)
async def post_user_with_password(user: UserCreate):
    new_user = UserResponse(id=1, username=user.username, email=user.email)
    return new_user


@router.get("/users/{username}")
async def get_user_by_username(username: str):
    if username == "not_found":
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "message": "User found"}


@router.get("/users/", response_model=List[UserResponse])
async def get_users_list(skip: int = 0, limit: int = 10):
    users = [
        UserResponse(id=i, username=f"user{i}", email=f"user{i}@example.com")
        for i in range(skip, skip + limit)
    ]
    return users
