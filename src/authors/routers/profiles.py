from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.schemas import Profile, ProfileCreate, ProfileUpdate
from src.dependencies import get_db
from src.authors import crud

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=Profile)
async def add_profile(profile_create: ProfileCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.create_profile(db=db, profile_create=profile_create)
