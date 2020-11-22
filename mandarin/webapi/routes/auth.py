import fastapi as f

from ...database import *
from .. import models
from mandarin.webapi.dependencies.auth import *


router_auth = f.APIRouter()


@router_auth.get(
    "/token",
    summary="Validate the current access token.",
    responses={
        **login_error,
    },
    response_model=models.UserOutput
)
def access_token(
    payload: dict = f.Depends(dependency_access_token)
):
    """
    Returns the payload obtained by getting the `/userinfo` endpoint of the authentication provider with the passed
    bearer token.

    Can be used to debug the authentication process.
    """
    return payload


@router_auth.get(
    "/user",
    summary="Get info about the logged in user.",
    responses={
        **login_error
    },
    response_model=models.UserOutput
)
def current_user(
    ls: LoginSession = f.Depends(dependency_login_session)
):
    """
    Returns information about the user that matches the passed bearer token.

    Can be used to debug the authentication process.
    """
    return ls.user


__all__ = (
    "router_auth",
)
