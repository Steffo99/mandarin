import fastapi as f

from ...database import *
from ..models.database import *
from mandarin.webapi.dependencies.auth import *


router_auth = f.APIRouter()


@router_auth.get(
    "/token",
    summary="Validate the current access token.",
    responses={
        **login_error,
    },
    response_model=MUser
)
def access_token(
    payload: dict = f.Depends(dependency_access_token)
) -> MUser:
    return MUser(**payload)


@router_auth.get(
    "/user",
    summary="Get info about the logged in user.",
    responses={
        **login_error
    },
    response_model=MUser
)
def current_user(
    ls: LoginSession = f.Depends(dependency_login_session)
) -> MUser:
    return MUser.from_orm(ls.user)


__all__ = (
    "router_auth",
)
