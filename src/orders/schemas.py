from pydantic import BaseModel, ConfigDict
from src.authors.schemas import Author
from src.books.schemas import Book


class OrderBase(BaseModel):
    pass


class OrderCreate(OrderBase):
    author_id: int
    book_ids: list[int]


class Order(OrderBase):
    id: int
    author: Author
    books: list[Book]

    model_config = ConfigDict(from_attributes=True)
