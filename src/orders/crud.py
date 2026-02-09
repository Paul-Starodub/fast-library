from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src import Order, Book
from src.orders.models import BookOrder
from src.orders.schemas import OrderCreate


async def get_orders(db: AsyncSession) -> list[Order]:
    stmt: Result = await db.execute(
        select(Order).options(
            joinedload(Order.author),
            selectinload(Order.books).joinedload(BookOrder.book).joinedload(Book.author),
            selectinload(Order.books).joinedload(BookOrder.book).joinedload(Book.genre),
        )
    )
    return list(stmt.scalars().all())


async def add_order(db: AsyncSession, order_in: OrderCreate) -> Order:
    order = Order(author_id=order_in.author_id)
    db.add(order)
    book_ids = [b.book_id for b in order_in.books]
    result = await db.execute(select(Book).where(Book.id.in_(book_ids)))
    books_map = {b.id: b for b in result.scalars().all()}
    if len(books_map) != len(set(book_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more books not found")
    for item in order_in.books:
        order.books.append(BookOrder(book=books_map[item.book_id], quantity=item.quantity))
    await db.commit()
    result = (
        select(Order)
        .where(Order.id == order.id)
        .options(
            joinedload(Order.author),
            selectinload(Order.books).joinedload(BookOrder.book).joinedload(Book.author),
            selectinload(Order.books).joinedload(BookOrder.book).joinedload(Book.genre),
        )
    )
    order = await db.scalar(result)
    return order


async def delete_order(db: AsyncSession, order_id: int) -> None:
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    await db.delete(order)
    await db.commit()
