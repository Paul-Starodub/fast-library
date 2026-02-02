from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import Base

if TYPE_CHECKING:
    from src.books.models import Book


class Author(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True)
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"
