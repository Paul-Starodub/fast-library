from pydantic import BaseModel, ConfigDict, Field
from src.authors.schemas import Author
from src.books.schemas import Book


class OrderBase(BaseModel):
    pass


class OrderBookIn(BaseModel):
    book_id: int
    quantity: int = Field(ge=1)


class OrderBook(BaseModel):
    book: Book
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(OrderBase):
    author_id: int
    books: list[OrderBookIn]


class Order(OrderBase):
    id: int
    author: Author
    book_orders: list[OrderBook]

    model_config = ConfigDict(from_attributes=True)
