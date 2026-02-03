from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.mixins import UserRelationMixin
from src.models import Base

if TYPE_CHECKING:
    from src.books.models import Book


# Association object
class BookOrder(Base):
    __tablename__ = "books_orders"
    __table_args__ = (UniqueConstraint("book_id", "order_id", name="idx_unique_book_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")

    book: Mapped["Book"] = relationship(back_populates="orders")
    order: Mapped["Order"] = relationship(back_populates="books")


class Order(UserRelationMixin, Base):
    _user_back_populate = "orders"
    ordered_at: Mapped[datetime] = mapped_column(server_default=func.now(), default=datetime.utcnow)

    books: Mapped[list[BookOrder]] = relationship(back_populates="order")

    def __repr__(self) -> str:
        return f"Order: {self.id}"
