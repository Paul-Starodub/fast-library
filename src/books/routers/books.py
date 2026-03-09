from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, status, Depends, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.books import crud, schemas
from src.books.schemas import BookFormData
from src.dependencies import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[schemas.Book])
async def get_books(db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_book.get_books(db)


@router.get("/{book_id}/", response_model=schemas.BookWithTags)
async def get_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int):
    return await crud.crud_book.get_book(db, book_id)


@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookFormData = Depends(BookFormData.as_form),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await crud.crud_book.create_book(
        db=db,
        file=file,
        genre_id=data.genre_id,
        author_id=data.author_id,
        title=data.title,
        rating=data.rating,
        date_published=data.date_published,
    )


@router.put("/{book_id}/", response_model=schemas.Book, status_code=status.HTTP_200_OK)
async def update_book(
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: int,
    genre_id: int = Form(...),
    author_id: int = Form(...),
    title: str = Form(...),
    rating: int = Form(...),
    date_published: datetime = Form(...),
    file: UploadFile = File(...),
):
    return await crud.crud_book.update_book(
        db=db,
        file=file,
        genre_id=genre_id,
        author_id=author_id,
        title=title,
        rating=rating,
        date_published=date_published,
        book_id=book_id,
    )


@router.patch("/{book_id}/", response_model=schemas.Book, status_code=status.HTTP_200_OK)
async def update_book_partial(
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: int,
    genre_id: int = Form(...),
    author_id: int = Form(...),
    title: str = Form(...),
    rating: int = Form(...),
    date_published: datetime = Form(...),
    file: UploadFile = File(...),
):
    return await crud.crud_book.update_book(
        db=db,
        file=file,
        genre_id=genre_id,
        author_id=author_id,
        title=title,
        rating=rating,
        date_published=date_published,
        book_id=book_id,
        partial=True,
    )


@router.delete("/{book_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int):
    return await crud.crud_book.delete_book(db, book_id)


@router.put("/{book_id}/tags/{tag_id}/", response_model=schemas.BookWithTags)
async def attach_tag(db: Annotated[AsyncSession, Depends(get_db)], book_id: int, tag_id: int):
    return await crud.crud_book.attach_tag_to_book(db=db, book_id=book_id, tag_id=tag_id)
