from fastapi import HTTPException, status
from sqlalchemy import select, and_, insert, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from src.books import models
from src.books.schemas import GenreCreate, GenreUpdate, BookCreate, BookUpdate, TagCreate, TagUpdate


class GenreCRUD:
    @staticmethod
    async def get_genres(db: AsyncSession) -> list[models.Genre]:
        stmt = await db.execute(select(models.Genre).order_by(models.Genre.name))
        return list(stmt.scalars().all())

    @staticmethod
    async def get_genre(db: AsyncSession, genre_id: int) -> models.Genre:
        stmt = await db.execute(select(models.Genre).where(models.Genre.id == genre_id))
        genre = stmt.scalars().first()
        if genre:
            return genre
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")

    @staticmethod
    async def get_genre_with_books(db: AsyncSession, genre_id: int) -> models.Genre:
        stmt = (
            select(models.Genre)
            .where(models.Genre.id == genre_id)
            .options(selectinload(models.Genre.books).joinedload(models.Book.author))
        )
        result = await db.execute(stmt)
        genre = result.scalars().first()
        if genre:
            return genre
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")

    @staticmethod
    async def create_genre(db: AsyncSession, genre_create: GenreCreate) -> models.Genre:
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
    async def update_genre(db: AsyncSession, genre_update: GenreUpdate, genre_id: int) -> models.Genre:
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
    async def delete_genre(db: AsyncSession, genre_id: int) -> None:
        stmt = await db.execute(select(models.Genre).where(models.Genre.id == genre_id))
        genre = stmt.scalar_one_or_none()
        if not genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
        await db.delete(genre)
        await db.commit()


class BookCRUD:
    @staticmethod
    async def get_books(db: AsyncSession) -> list[models.Book]:
        stmt = await db.execute(
            select(models.Book)
            .options(joinedload(models.Book.genre), joinedload(models.Book.author), selectinload(models.Book.tags))
            .order_by(models.Book.title)
        )
        return list(stmt.scalars().all())

    @staticmethod
    async def get_book(db: AsyncSession, book_id: int) -> models.Book:
        stmt = await db.execute(
            select(models.Book)
            .where(models.Book.id == book_id)
            .options(joinedload(models.Book.genre), joinedload(models.Book.author), selectinload(models.Book.tags))
        )
        book = stmt.scalars().first()
        if book:
            return book
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    @staticmethod
    async def create_book(db: AsyncSession, book_create: BookCreate) -> models.Book:
        stmt = select(models.Book.id).where(models.Book.title == book_create.title)
        existing_book = await db.execute(stmt)
        if existing_book.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book with this title already exists")
        book = models.Book(**book_create.model_dump())
        db.add(book)
        await db.commit()
        await db.refresh(book, attribute_names=["genre", "author"])
        return book

    @staticmethod
    async def update_book(
        db: AsyncSession, book_id: int, book_update: BookUpdate, partial: bool = False
    ) -> models.Book:
        stmt = select(models.Book).where(models.Book.id == book_id)
        result = await db.execute(stmt)
        book = result.scalar_one_or_none()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        update_data = book_update.model_dump(exclude_unset=partial)
        new_title = update_data.get("title")
        if new_title and new_title != book.title:
            stmt = select(models.Book.id).where(
                models.Book.title == new_title,
                models.Book.id != book_id,
            )
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Book with this title already exists",
                )
        for field, value in update_data.items():
            setattr(book, field, value)
        await db.commit()
        await db.refresh(book, attribute_names=["genre", "author"])
        return book

    @staticmethod
    async def delete_book(db: AsyncSession, book_id: int) -> None:
        stmt = await db.execute(select(models.Book).where(models.Book.id == book_id))
        book = stmt.scalars().first()
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        await db.delete(book)
        await db.commit()

    @staticmethod
    async def attach_tag_to_book(db: AsyncSession, book_id: int, tag_id: int) -> models.Book:
        stmt = select(models.Book, exists(select(1).where(models.Tag.id == tag_id))).where(models.Book.id == book_id)
        result = await db.execute(stmt)
        row = result.first()
        if not row or not row[0]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        if not row[1]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        check_stmt = (
            select(1)
            .where(
                and_(
                    models.book_tag_association_table.c.book_id == book_id,
                    models.book_tag_association_table.c.tag_id == tag_id,
                )
            )
            .exists()
        )
        if await db.scalar(select(check_stmt)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag for this book already exists")
        stmt = insert(models.book_tag_association_table).values(book_id=book_id, tag_id=tag_id)
        await db.execute(stmt)
        await db.commit()
        stmt = (
            select(models.Book)
            .options(joinedload(models.Book.genre), joinedload(models.Book.author), selectinload(models.Book.tags))
            .where(models.Book.id == book_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()


class TagCrud:
    @staticmethod
    async def get_all_tags(db: AsyncSession) -> list[models.Tag]:
        stmt = await db.execute(select(models.Tag).order_by(models.Tag.name))
        tags = stmt.scalars().all()
        return list(tags)

    @staticmethod
    async def get_tag_by_id(db: AsyncSession, tag_id: int) -> models.Tag:
        stmt = await db.execute(select(models.Tag).where(models.Tag.id == tag_id))
        tag = stmt.scalar_one_or_none()
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        return tag

    @staticmethod
    async def create_tag(db: AsyncSession, tag_create: TagCreate) -> models.Tag:
        tag = models.Tag(**tag_create.model_dump())
        db.add(tag)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
        await db.refresh(tag)
        return tag

    @staticmethod
    async def update_tag(db: AsyncSession, tag_id: int, tag_update: TagUpdate) -> models.Tag:
        tag = await db.scalar(select(models.Tag).where(models.Tag.id == tag_id))
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        for field, value in tag_update.model_dump().items():
            setattr(tag, field, value)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
        await db.refresh(tag)
        return tag

    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: int) -> None:
        tag = await db.scalar(select(models.Tag).where(models.Tag.id == tag_id))
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        await db.delete(tag)
        await db.commit()


crud_genre = GenreCRUD()

crud_book = BookCRUD()

crud_tag = TagCrud()
