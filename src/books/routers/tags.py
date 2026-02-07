from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.books import schemas, crud
from src.dependencies import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[schemas.Tag])
async def get_tags(db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_tag.get_all_tags(db)


@router.get("/{tag_id}/", response_model=schemas.Tag)
async def get_tag(tag_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_tag.get_tag_by_id(db=db, tag_id=tag_id)


@router.post("/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(tag_create: schemas.TagCreate, db: AsyncSession = Depends(get_db)):
    return await crud.crud_tag.create_tag(db=db, tag_create=tag_create)


@router.put("/{tag_id}/", response_model=schemas.Tag)
async def update_tag(tag_id: int, tag_update: schemas.TagUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.crud_tag.update_tag(db=db, tag_id=tag_id, tag_update=tag_update)


@router.delete("/{tag_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_tag.delete_tag(db=db, tag_id=tag_id)
