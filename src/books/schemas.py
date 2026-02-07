from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.authors.schemas import AuthorPublic


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GenreBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]


class GenreCreate(GenreBase):
    pass


class GenreUpdate(GenreBase):
    pass


class Genre(GenreBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=100)]
    rating: Annotated[int, Field(ge=0, le=5)]
    date_published: Optional[datetime]
    image_file: str | None = Field(default=None, min_length=1, max_length=200)


class BookCreate(BookBase):
    genre_id: Annotated[int, Field(ge=1)]
    author_id: Annotated[int, Field(ge=1)]


class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    rating: int | None = Field(None, ge=0, le=5)
    date_published: datetime | None = None
    image_file: str | None = Field(None, min_length=1, max_length=200)
    genre_id: int | None = Field(None, ge=1)
    author_id: int | None = Field(None, ge=1)


class Book(BookBase):
    id: int
    image_path: str
    genre: Genre | None
    author: AuthorPublic | None
    tags: list[Tag] | None

    model_config = ConfigDict(from_attributes=True)


class BookAuthor(BookBase):
    id: int
    image_path: str
    author: AuthorPublic | None

    model_config = ConfigDict(from_attributes=True)


class GenreBook(Genre):
    books: list[BookAuthor]
