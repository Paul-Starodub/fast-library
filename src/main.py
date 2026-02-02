from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.books.routers import genres_router, books_router
from src import Author, Profile, Book, Genre  # noqa: F401 - Import to register models

BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI()
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(genres_router)
app.include_router(books_router)


@app.get("/")
def root() -> dict:
    return {"message": "Hello World"}
