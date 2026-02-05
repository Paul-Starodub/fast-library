from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors import crud
from src.authors.schemas import AuthorPrivate, AuthorCreate
from src.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=AuthorPrivate, status_code=status.HTTP_201_CREATED)
async def create_author(db: Annotated[AsyncSession, Depends(get_db)], author: AuthorCreate):

    return await crud.create_author(db=db, author=author)
