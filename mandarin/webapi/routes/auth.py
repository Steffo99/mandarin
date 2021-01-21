import fastapi as f

from .. import dependencies
from .. import models
from .. import responses
from ...config import lazy_config

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


@router_auth.get(
    "/config",
    summary="Get the current authentication settings.",
    response_model=models.AuthConfig,
)
def config():
    """
    Returns the authentication config settings of this Mandarin instance.
    """
    return models.AuthConfig(
        authorization=lazy_config.e["auth.authorization"],
        device=lazy_config.e["auth.device"],
        token=lazy_config.e["auth.token"],
        refresh=lazy_config.e["auth.refresh"],
        userinfo=lazy_config.e["auth.userinfo"],
        openidcfg=lazy_config.e["auth.openidcfg"],
        jwks=lazy_config.e["auth.jwks"],
    )


__all__ = (
    "router_auth",
)
