from pydantic import BaseModel, ConfigDict, EmailStr


class AuthorBase(BaseModel):
    username: str
    image_file: str | None = None


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):  # for learing purpose
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True
