from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root() -> dict:
    return {"message": "Hello World"}
