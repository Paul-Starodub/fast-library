from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.authors.models import Author


class UserRelationMixin:
    _user_id_unique: bool = False
    _user_back_populate: str | None = None
    _user_id_nullable: bool = False

    # Don't use classmethod for user_id and user attributes
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("authors.id"), unique=cls._user_id_unique, nullable=cls._user_id_nullable)

    @declared_attr
    def user(cls) -> Mapped["Author"]:
        return relationship("Author", back_populates=cls._user_back_populate)
