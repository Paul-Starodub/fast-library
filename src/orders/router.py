from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.orders import crud
from src.orders.schemas import Order, OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[Order])
async def get_orders(db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.get_orders(db=db)


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(db: Annotated[AsyncSession, Depends(get_db)], order_in: OrderCreate):
    return await crud.add_order(db=db, order_in=order_in)


@router.delete("/{order_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(db: Annotated[AsyncSession, Depends(get_db)], order_id: int):
    return await crud.delete_order(db=db, order_id=order_id)
