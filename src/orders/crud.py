from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from src import Order, Book
from src.orders.schemas import OrderCreate


async def get_orders(db: AsyncSession) -> list[Order]:
    stmt: Result = await db.execute(
        select(Order).options(selectinload(Order.books).joinedload(Book.genre), joinedload(Order.author))
    )
    return list(stmt.scalars().all())


async def add_order(db: AsyncSession, order_in: OrderCreate) -> Order:
    order = Order(author_id=order_in.author_id)
    db.add(order)
    stmt = select(Book).where(Book.id.in_(order_in.book_ids))
    result = await db.execute(stmt)
    books = result.scalars().all()
    if len(books) != len(set(order_in.book_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more books not found")
    order.books.extend(books)
    await db.commit()
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(
            joinedload(Order.author),
            selectinload(Order.books).joinedload(Book.genre),
        )
    )
    return result.scalar_one()


async def delete_order(db: AsyncSession, order_id: int) -> None:
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await db.delete(order)
    await db.commit()
