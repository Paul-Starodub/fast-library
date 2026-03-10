from datetime import datetime
from typing import Annotated

from fastapi import Form

from src.books.schemas import BookFormData, BookUpdate


async def book_form_data(
    genre_id: Annotated[int, Form()],
    author_id: Annotated[int, Form()],
    title: Annotated[str, Form()],
    rating: Annotated[int, Form()],
    date_published: Annotated[datetime | None, Form()] = None,
) -> BookFormData:
    return BookFormData(
        genre_id=genre_id,
        author_id=author_id,
        title=title,
        rating=rating,
        date_published=date_published,
    )


async def book_update_form_data(
    genre_id: Annotated[int | None, Form()] = None,
    author_id: Annotated[int | None, Form()] = None,
    title: Annotated[str | None, Form()] = None,
    rating: Annotated[int | None, Form()] = None,
    date_published: Annotated[datetime | None, Form()] = None,
) -> BookUpdate:
    return BookUpdate(
        genre_id=genre_id,
        author_id=author_id,
        title=title,
        rating=rating,
        date_published=date_published,
    )
