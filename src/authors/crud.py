from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.authors import models
from src.authors.schemas import AuthorCreate, AuthorUpdate, Token, ProfileCreate
from src.authors.security import hash_password, oauth2_scheme, verify_access_token, verify_password, create_access_token
from src.config import settings
from src.dependencies import get_db


async def create_author(author: AuthorCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> models.Author:
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


async def update_author(db: AsyncSession, author_id: int, author_update: AuthorUpdate) -> models.Author:
    result = await db.execute(select(models.Author).where(models.Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    update_data = author_update.model_dump(exclude_unset=True)
    if "email" in update_data:
        result = await db.execute(
            select(models.Author.id).where(
                func.lower(models.Author.email) == update_data["email"].lower(),
                models.Author.id != author_id,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    if "username" in update_data:
        result = await db.execute(
            select(models.Author.id).where(
                func.lower(models.Author.username) == update_data["username"].lower(),
                models.Author.id != author_id,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    if "password" in update_data:
        author.password_hash = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(author, field, value)
    await db.commit()
    await db.refresh(author)
    return author


async def delete_author_by_id(db: AsyncSession, author_id: int) -> None:
    stmt = await db.execute(select(models.Author).where(models.Author.id == author_id))
    author = stmt.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    await db.delete(author)
    await db.commit()


async def login_author_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    result = await db.execute(
        select(models.Author).where(
            func.lower(models.Author.email) == form_data.username.lower(),
        ),
    )
    author = result.scalar_one_or_none()
    if not author or not verify_password(form_data.password, author.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(author.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


async def get_current_author(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]
) -> models.Author:
    author_id = verify_access_token(token)
    authentication_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if author_id is None:
        raise authentication_exc
    try:
        author_id_int = int(author_id)
    except (TypeError, ValueError):
        raise authentication_exc
    result = await db.execute(
        select(models.Author).where(models.Author.id == author_id_int),
    )
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Author not found", headers={"WWW-Authenticate": "Bearer"}
        )
    return author


async def create_profile(profile_create: ProfileCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> models.Profile:
    stmt = select(models.Profile.id).where(models.Profile.author_id == profile_create.author_id)
    existing_profile = await db.execute(stmt)
    if existing_profile.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile for this author already exists")
    profile = models.Profile(**profile_create.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile, attribute_names=["author"])
    return profile


async def get_all_profiles(db: Annotated[AsyncSession, Depends(get_db)]) -> list[models.Profile]:
    stmt = select(models.Profile).options(joinedload(models.Profile.author)).order_by(models.Profile.author_id)
    profiles = await db.execute(stmt)
    return list(profiles.scalars().all())


async def get_current_profile_for_author(db: Annotated[AsyncSession, Depends(get_db)], author_id: int):
    stmt = await db.execute(
        select(models.Profile)
        .where(models.Profile.author_id == author_id)
        .options(joinedload(models.Profile.author))
    )
    profile = stmt.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile
