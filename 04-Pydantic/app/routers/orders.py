# app/routers/orders.py

from fastapi import APIRouter
from ..schemas import Order

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post("/", response_model=Order)
async def post_order(order: Order):
    # Here you would typically save the order to the database
    return order
