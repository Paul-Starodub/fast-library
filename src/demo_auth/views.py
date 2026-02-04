import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])


# basic authentication
security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {"username": credentials.username, "password": credentials.password}


usernames_to_passwords = {"admin": "admin", "john": "password"}


def get_auth_user_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    correct_password = usernames_to_passwords.get(credentials.username)
    if correct_password is None:
        raise unauthorized_exc
    if not secrets.compare_digest(credentials.password.encode("utf-8"), correct_password.encode("utf-8")):
        raise unauthorized_exc
    return credentials.username


@router.get("/basic-auth-username/")
def demo_basic_auth_username(auth_username: str = Depends(get_auth_user_username)):
    return {"message": f"Hi!{auth_username}", "username": auth_username}
