from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.books import schemas, crud
from src.dependencies import get_db

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=list[schemas.Genre])
async def get_genres(db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_genre.get_genres(db)


@router.get("/{genre_id}/", response_model=schemas.Genre)
async def get_genre(genre_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_genre.get_genre(db=db, genre_id=genre_id)


@router.get("/genres/{genre_id}/with_books/", response_model=schemas.GenreBook)
async def get_genre_with_books(genre_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_genre.get_genre_with_books(db=db, genre_id=genre_id)


@router.post("/", response_model=schemas.Genre, status_code=status.HTTP_201_CREATED)
async def create_genre(genre_create: schemas.GenreCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_genre.create_genre(db=db, genre_create=genre_create)


@router.patch("/{genre_id}/", response_model=schemas.Genre)
async def update_genre(genre_update: schemas.GenreUpdate, genre_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_genre.update_genre(db=db, genre_update=genre_update, genre_id=genre_id)


@router.delete("/{genre_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_genre.delete_genre(db=db, genre_id=genre_id)
