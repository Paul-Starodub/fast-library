from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.books.routers import genres_router, books_router, tags_router
from src.orders.router import router as orders_router
from src.demo_auth.views import router as demo_auth_router
from src.authors.routers import authors_router, profiles_router

BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI()
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(genres_router)
app.include_router(books_router)
app.include_router(orders_router)
app.include_router(demo_auth_router)
app.include_router(authors_router)
app.include_router(tags_router)
app.include_router(profiles_router)


@app.get("/")
def root() -> dict:
    return {"message": "Hello World"}
