from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors import crud, models
from src.authors.schemas import Profile, ProfileCreate, ProfileUpdate
from src.dependencies import get_db

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/", response_model=list[Profile])
async def get_profiles(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_profiles(db=db)


@router.post("/create/", response_model=Profile, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_create: ProfileCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_author: Annotated[models.Author, Depends(crud.get_current_author)],
):
    profile_create.author_id = current_author.id
    return await crud.create_profile(db=db, profile_create=profile_create)


@router.get("/me/", response_model=Profile)
async def get_my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_author: Annotated[models.Author, Depends(crud.get_current_author)],
):
    return await crud.get_profile_by_author_id(db=db, author_id=current_author.id)


@router.get("/{author_id}/", response_model=Profile)
async def get_profile(author_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_profile_by_author_id(db=db, author_id=author_id)


@router.patch("/update/", response_model=Profile)
async def update_my_profile(
    profile_update: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_author: Annotated[models.Author, Depends(crud.get_current_author)],
):
    profile = await crud.get_profile_by_author_id(db=db, author_id=current_author.id)
    return await crud.update_profile(profile_update=profile_update, profile_id=profile.id, db=db)


@router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_author: Annotated[models.Author, Depends(crud.get_current_author)],
):
    profile = await crud.get_profile_by_author_id(db=db, author_id=current_author.id)
    await crud.delete_profile_by_id(profile_id=profile.id, db=db)
    return None
