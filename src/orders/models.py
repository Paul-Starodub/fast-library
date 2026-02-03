from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.mixins import UserRelationMixin
from src.models import Base

if TYPE_CHECKING:
    from src.books.models import Book


# book_order_association_table = Table(
#     "books_orders",
#     Base.metadata,
#     Column("id", Integer, primary_key=True),
#     Column("book_id", Integer, ForeignKey("books.id"), nullable=False),
#     Column("order_id", Integer, ForeignKey("orders.id"), nullable=False),
#     UniqueConstraint("book_id", "order_id", name="unique_book_order"),
# )  # simple version


# Association object
class BookOrder(Base):
    __tablename__ = "books_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")

    book: Mapped["Book"] = relationship("Book", back_populates="book_orders")
    order: Mapped["Order"] = relationship("Order", back_populates="book_orders")


class Order(UserRelationMixin, Base):
    _user_back_populate = "orders"
    ordered_at: Mapped[datetime] = mapped_column(server_default=func.now(), default=datetime.utcnow)

    # books: Mapped[list["Book"]] = relationship(secondary=book_order_association_table, back_populates="orders")
    book_orders: Mapped[list[BookOrder]] = relationship(
        "BookOrder", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Order: {self.id}"
