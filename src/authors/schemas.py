from pydantic import BaseModel, ConfigDict


class AuthorBase(BaseModel):
    username: str
    image_file: str | None = None


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
