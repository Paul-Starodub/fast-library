from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, func, Table, Column, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.mixins import UserRelationMixin
from src.models import Base

if TYPE_CHECKING:
    from src.orders.models import BookOrder

book_tag_association_table = Table(
    "book_tags",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Genre(Base):
    name: Mapped[str] = mapped_column(String(50), unique=True)
    books: Mapped[list["Book"]] = relationship(back_populates="genre", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class Tag(Base):
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), default=datetime.utcnow)

    books: Mapped[list["Book"]] = relationship(secondary=book_tag_association_table, back_populates="tags")

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name={self.name})"


class Book(UserRelationMixin, Base):
    _user_back_populate = "books"
    title: Mapped[str] = mapped_column(String(100), unique=True)
    rating: Mapped[int] = mapped_column(default=0)
    date_published: Mapped[datetime]
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))

    genre: Mapped["Genre"] = relationship(back_populates="books")
    tags: Mapped[list["Tag"]] = relationship(secondary=book_tag_association_table, back_populates="books")
    orders: Mapped[list["BookOrder"]] = relationship(back_populates="book")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/book_pics/{self.image_file}"
        return "/static/book_pics/default.jpg"

    def __repr__(self) -> str:
        return f"Book(id={self.id}, rating={self.rating}, date_published={self.date_published}"
