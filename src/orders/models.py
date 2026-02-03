from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.mixins import UserRelationMixin
from src.models import Base

if TYPE_CHECKING:
    from src.books.models import Book


book_order_association_table = Table(
    "books_orders",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), nullable=False),
    Column("order_id", Integer, ForeignKey("orders.id"), nullable=False),
    Column("quantity", Integer, default=1, nullable=False, server_default="1"),
    UniqueConstraint("book_id", "order_id", name="unique_book_order"),
)


class Order(UserRelationMixin, Base):
    _user_back_populate = "orders"
    ordered_at: Mapped[datetime] = mapped_column(server_default=func.now(), default=datetime.utcnow)

    books: Mapped[list["Book"]] = relationship(secondary=book_order_association_table, back_populates="orders")

    def __repr__(self) -> str:
        return f"Order: {self.id}"
