from typing import Annotated

from fastapi import APIRouter, status, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.books import crud, schemas
from src.books.dependencies import book_form_data, book_update_form_data
from src.books.schemas import BookFormData, BookUpdate
from src.dependencies import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[schemas.Book])
async def get_books(db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.crud_book.get_books(db)


@router.get("/{book_id}/", response_model=schemas.BookWithTags)
async def get_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int):
    return await crud.crud_book.get_book(db, book_id)


@router.post("/")
async def create_book(
    data: BookFormData = Depends(book_form_data),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await crud.crud_book.create_book(db=db, file=file, **data.model_dump())


# @router.put("/{book_id}/", response_model=schemas.Book, status_code=status.HTTP_200_OK)
# async def update_book(
#     db: Annotated[AsyncSession, Depends(get_db)],
#     book_id: int,
#     genre_id: int = Form(...),
#     author_id: int = Form(...),
#     title: str = Form(...),
#     rating: int = Form(...),
#     date_published: datetime = Form(...),
#     file: UploadFile = File(...),
# ):
#     return await crud.crud_book.update_book(
#         db=db,
#         file=file,
#         genre_id=genre_id,
#         author_id=author_id,
#         title=title,
#         rating=rating,
#         date_published=date_published,
#         book_id=book_id,
#     )
#
#
# @router.patch("/{book_id}/", response_model=schemas.Book, status_code=status.HTTP_200_OK)
# async def update_book_partial(
#     db: Annotated[AsyncSession, Depends(get_db)],
#     book_id: int,
#     genre_id: int = Form(...),
#     author_id: int = Form(...),
#     title: str = Form(...),
#     rating: int = Form(...),
#     date_published: datetime = Form(...),
#     file: UploadFile = File(...),
# ):
#     return await crud.crud_book.update_book(
#         db=db,
#         file=file,
#         genre_id=genre_id,
#         author_id=author_id,
#         title=title,
#         rating=rating,
#         date_published=date_published,
#         book_id=book_id,
#         partial=True,
#     )


@router.put("/{book_id}/", response_model=schemas.Book)
async def update_book(
    book_id: int,
    data: BookFormData = Depends(book_form_data),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await crud.crud_book.update_book(
        db=db,
        file=file,
        book_id=book_id,
        **data.model_dump(),
    )


@router.patch("/{book_id}/", response_model=schemas.Book)
async def update_book_partial(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    file: UploadFile | None = File(None),
    data: BookUpdate = Depends(book_update_form_data),
):
    return await crud.crud_book.update_book(
        db=db,
        file=file,
        book_id=book_id,
        partial=True,
        **data.model_dump(exclude_unset=True),
    )


@router.delete("/{book_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: Annotated[AsyncSession, Depends(get_db)], book_id: int):
    return await crud.crud_book.delete_book(db, book_id)


@router.put("/{book_id}/tags/{tag_id}/", response_model=schemas.BookWithTags)
async def attach_tag(db: Annotated[AsyncSession, Depends(get_db)], book_id: int, tag_id: int):
    return await crud.crud_book.attach_tag_to_book(db=db, book_id=book_id, tag_id=tag_id)
