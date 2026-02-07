from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AuthorBase(BaseModel):
    username: str
    image_file: str | None = None


class AuthorCreate(AuthorBase):
    password: str = Field(min_length=8)
    email: EmailStr = Field(max_length=50)


class AuthorUpdate(BaseModel):
    username: str | None = None
    image_file: str | None = None
    email: EmailStr = Field(max_length=50)
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None
    is_superuser: bool | None = None


class AuthorPublic(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str


class AuthorPrivate(AuthorPublic):
    email: EmailStr = Field(max_length=50)
    is_active: bool
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):  # for learning purpose
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


class ProfileBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: int
    author: AuthorPrivate

    model_config = ConfigDict(from_attributes=True)
