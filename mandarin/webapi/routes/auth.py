import fastapi as f

from ...database import *
from ..models.database import *
from mandarin.webapi.dependencies.auth import *


router_auth = f.APIRouter()


@router_auth.get(
    "/token",
    summary="Validate the current access token.",
    responses={
        401: {"description": "Not logged in"},
    },
    response_model=dict
)
def access_token(payload: dict = f.Depends(validate_access_token)):
    return payload


@router_auth.get(
    "/user",
    summary="Get info about the logged in user.",
    responses={
        401: {"description": "Not logged in"},
    },
    response_model=MUser
)
def current_user(user: User = f.Depends(find_or_create_user)):
    return MUser.from_orm(user)


__all__ = (
    "router_auth",
)
