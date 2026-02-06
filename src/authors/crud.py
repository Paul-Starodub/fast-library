from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors import models
from src.authors.schemas import AuthorCreate
from src.authors.security import hash_password
from src.dependencies import get_db


async def create_author(author: AuthorCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Author).where(
            func.lower(models.Author.username) == author.username.lower(),
        ),
    )
    existing_author = result.scalar_one_or_none()
    if existing_author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    result = await db.execute(
        select(models.Author).where(func.lower(models.Author.email) == author.email.lower()),
    )
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_author = models.Author(
        username=author.username,
        email=author.email.lower(),
        password_hash=hash_password(author.password),
    )
    db.add(new_author)
    await db.commit()
    await db.refresh(new_author)
    return new_author


async def get_authors(db: AsyncSession, limit, offset) -> list[models.Author]:
    stmt = await db.execute(select(models.Author).order_by(models.Author.username).limit(limit).offset(offset))
    return list(stmt.scalars().all())


async def get_author(db: AsyncSession, author_id) -> models.Author | None:
    stmt = await db.execute(select(models.Author).where(models.Author.id == author_id))
    author = stmt.scalar_one_or_none()
    if author:
        return author
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
