from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.mixins import UserRelationMixin
from src.models import Base

if TYPE_CHECKING:
    from src.books.models import Book
    from src.orders.models import Order


class Author(Base):
    email: Mapped[EmailStr] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    profile: Mapped["Profile"] = relationship(back_populates="author")
    orders: Mapped[list["Order"]] = relationship(back_populates="author")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

    def __repr__(self) -> str:
        return f"Author(id={self.id}, username={self.username})"


class Profile(UserRelationMixin, Base):
    _user_id_unique = True  # for a one-to-one relationship
    _user_back_populate = "profile"
    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None]

    def __repr__(self) -> str:
        return f"Profile(id={self.id}, first_name={self.first_name}, last_name={self.last_name})"
