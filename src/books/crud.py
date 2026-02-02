from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.books import models
from src.books.schemas import GenreCreate, GenreUpdate, BookCreate, BookUpdate


class GenreCRUD:
    @staticmethod
    async def get_genres(db: AsyncSession):
        stmt = await db.execute(select(models.Genre))
        return stmt.scalars().all()

    @staticmethod
    async def get_genre(db: AsyncSession, genre_id: int):
        stmt = await db.execute(select(models.Genre).where(models.Genre.id == genre_id))
        genre = stmt.scalars().first()
        if genre:
            return genre
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")

    @staticmethod
    async def create_genre(db: AsyncSession, genre_create: GenreCreate):
        genre = models.Genre(**genre_create.model_dump())
        db.add(genre)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Genre with this name already exists")
        await db.refresh(genre)
        return genre

    @staticmethod
    async def update_genre(db: AsyncSession, genre_update: GenreUpdate, genre_id: int):
        stmt = await db.execute(select(models.Genre).where(models.Genre.id == genre_id))
        genre = stmt.scalar_one_or_none()
        if not genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
        update_data = genre_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(genre, field, value)
        await db.commit()
        await db.refresh(genre)
        return genre

    @staticmethod
    async def delete_genre(db: AsyncSession, genre_id: int):
        stmt = await db.execute(select(models.Genre).where(models.Genre.id == genre_id))
        genre = stmt.scalar_one_or_none()
        if not genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
        await db.delete(genre)
        await db.commit()


class BookCRUD:
    @staticmethod
    async def get_books(db: AsyncSession):
        stmt = await db.execute(select(models.Book))
        return stmt.scalars().all()

    @staticmethod
    async def get_book(db: AsyncSession, book_id: int):
        stmt = await db.execute(select(models.Book).where(models.Book.id == book_id))
        book = stmt.scalars().first()
        if book:
            return book
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    @staticmethod
    async def create_book(db: AsyncSession, book_create: BookCreate):
        stmt = select(models.Book).where(models.Book.title == book_create.title)
        existing_book = await db.execute(stmt)
        if existing_book.one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book with this title already exists")
        book = models.Book(**book_create.model_dump())
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book

    @staticmethod
    async def update_book(db: AsyncSession, book_id: int, book_update: BookUpdate, partial: bool = False):
        stmt = await db.execute(select(models.Book).where(models.Book.id == book_id))
        book = stmt.scalars().first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        for field, value in book_update.model_dump(exclude_unset=partial).items():
            setattr(book, field, value)
        await db.commit()
        await db.refresh(book)
        return book

    @staticmethod
    async def delete_book(db: AsyncSession, book_id: int):
        stmt = await db.execute(select(models.Book).where(models.Book.id == book_id))
        book = stmt.scalars().first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        await db.delete(book)


crud_genre = GenreCRUD()

crud_book = BookCRUD()
