from typing import Annotated
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.books import crud, schemas
from src.dependencies import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[schemas.Book])
async def get_books(db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_book.get_books(db)


@router.get("/{book_id}/", response_model=schemas.Book)
async def get_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int):
    return await crud.crud_book.get_book(db, book_id)


@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
async def create_book(db: Annotated[AsyncSession, Depends(get_db)], book: schemas.BookCreate):
    return await crud.crud_book.create_book(db, book)


@router.put("/{book_id}/", response_model=schemas.Book, status_code=status.HTTP_200_OK)
async def update_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int, book_update: schemas.BookUpdate):
    return await crud.crud_book.update_book(db, book_id, book_update)


@router.patch("/{book_id}/", response_model=schemas.Book, status_code=status.HTTP_200_OK)
async def update_book_partial(
    db: Annotated[AsyncSession, Depends(get_db)], book_id: int, book_update: schemas.BookUpdate
):
    return await crud.crud_book.update_book(db, book_id, book_update, partial=True)


@router.delete("/{book_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int):
    return await crud.crud_book.delete_book(db, book_id)
