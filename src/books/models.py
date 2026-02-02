from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.models import Base

if TYPE_CHECKING:
    from src.authors.models import Author


class Genre(Base):
    name: Mapped[str] = mapped_column(String(50), unique=True)
    books: Mapped[list["Book"]] = relationship(back_populates="genre", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class Book(Base):
    title: Mapped[str] = mapped_column(String(100), unique=True)
    rating: Mapped[int] = mapped_column(default=0)
    date_published: Mapped[datetime]
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    genre: Mapped["Genre"] = relationship(back_populates="books")
    author: Mapped["Author"] = relationship(back_populates="books")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/book_pics/{self.image_file}"
        return "/static/book_pics/default.jpg"

    def __repr__(self) -> str:
        return f"Book(id={self.id}, rating={self.rating}, date_published={self.date_published}"
