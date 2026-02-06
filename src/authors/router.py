from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors import crud
from src.authors.schemas import AuthorPrivate, AuthorCreate, AuthorPublic, AuthorUpdate, Token
from src.authors.security import oauth2_scheme
from src.dependencies import get_db

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=AuthorPrivate, status_code=status.HTTP_201_CREATED)
async def create_author(db: Annotated[AsyncSession, Depends(get_db)], author: AuthorCreate):
    return await crud.create_author(db=db, author=author)


@router.get("/", response_model=list[AuthorPublic])
async def get_authors(db: Annotated[AsyncSession, Depends(get_db)], limit: int = 20, offset: int = 0):
    return await crud.get_authors(db=db, limit=limit, offset=offset)


@router.post("/login/", response_model=Token)
async def login_author(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return await crud.login_author_for_access_token(db=db, form_data=form_data)


@router.get("/me/", response_model=AuthorPrivate)
async def get_current_author(
    db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
):
    return await crud.get_current_author(db=db, token=token)


@router.get("/{author_id}/", response_model=AuthorPublic)
async def get_author(db: Annotated[AsyncSession, Depends(get_db)], author_id: int):
    return await crud.get_author(db=db, author_id=author_id)


@router.patch("/{author_id}/", response_model=AuthorPrivate)
async def update_author(db: Annotated[AsyncSession, Depends(get_db)], author_id: int, author_update: AuthorUpdate):
    return await crud.update_author(db=db, author_id=author_id, author_update=author_update)


@router.delete("/{author_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(db: Annotated[AsyncSession, Depends(get_db)], author_id: int):
    await crud.delete_author_by_id(db=db, author_id=author_id)
