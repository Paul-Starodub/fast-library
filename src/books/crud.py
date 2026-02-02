from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.books import models
from src.books.schemas import GenreCreate, GenreUpdate


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


crud_genre = GenreCRUD()
