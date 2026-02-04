import secrets
import uuid
from time import time
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from fastapi.security import HTTPBasicCredentials, HTTPBasic

router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])


# basic authentication
#################################

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {"username": credentials.username, "password": credentials.password}


usernames_to_passwords = {"admin": "admin", "john": "password"}


def get_auth_user_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
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


# token authentication
#########################################

static_auth_token_to_username = {
    "4e06982488643b1165480dbc8559594f6f4362b891416b1117a5d0bca50314d1": "admin",
    "c94179cd1f40ec02f214afd1914a38e206fd6b07794bd57ce3213b144502e0bd": "john",
}


def get_username_by_static_auth_token(static_auth_token: str = Header(alias="x-auth-token")) -> str:
    if username := static_auth_token_to_username.get(static_auth_token):
        return username
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")


@router.get("/some-http-header-auth-username/")
def demo_auth_some_http_header(username: str = Depends(get_username_by_static_auth_token)):
    return {"message": f"Hi!{username}", "username": username}


# cookie authorization
##################################

COOKIES: dict[str, dict[str, Any]] = {}
COOKIES_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def get_session_data(session_id: str = Cookie(alias=COOKIES_SESSION_ID_KEY)) -> dict[str, Any]:
    if session_id not in COOKIES:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return COOKIES[session_id]


@router.post("/login-cookie/")
def demo_auth_login_set_cookie(
    response: Response,
    auth_username: str = Depends(get_auth_user_username),
    # username: str = Depends(get_username_by_static_auth_token)
):
    session_id = generate_session_id()
    COOKIES[session_id] = {"username": auth_username, "login_at": int(time())}
    response.set_cookie(COOKIES_SESSION_ID_KEY, session_id)
    return {"result": "Ok"}


@router.get("/check-cookie/")
def demo_auth_check_cookie(user_session_data: dict = Depends(get_session_data)):
    username = user_session_data.get("username")
    return {"message": f"Hello {username}", **user_session_data}


@router.get("/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIES_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIES_SESSION_ID_KEY)
    username = user_session_data.get("username")
    return {"message": f"By {username}"}
