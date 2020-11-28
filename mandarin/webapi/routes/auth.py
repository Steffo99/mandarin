import fastapi as f

from ...database import tables
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses


router_auth = f.APIRouter()


@router_auth.get(
    "/token",
    summary="Validate the current access token.",
    responses={
        **responses.login_error,
    },
    response_model=models.UserOutput
)
def access_token(
    payload: dict = f.Depends(dependencies.dependency_access_token)
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
        **responses.login_error
    },
    response_model=models.UserOutput
)
def current_user(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session)
):
    """
    Returns information about the user that matches the passed bearer token.

    Can be used to debug the authentication process.
    """
    return ls.user


__all__ = (
    "router_auth",
)
