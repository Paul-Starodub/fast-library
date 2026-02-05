from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AuthorBase(BaseModel):
    username: str
    email: EmailStr = Field(max_length=120)
    image_file: str | None = None


class AuthorCreate(AuthorBase):
    password: str = Field(min_length=8)


class AuthorPublic(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str


class AuthorPrivate(AuthorPublic):
    email: EmailStr
    is_active: bool
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):  # for learing purpose
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True
