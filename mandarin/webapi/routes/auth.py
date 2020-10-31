import fastapi as f

from ...database import *
from ..utils.auth import *


router_auth = f.APIRouter()


@router_auth.get("/access_token")
def access_token(payload: dict = f.Depends(validate_access_token)):
    return payload


@router_auth.get("/current_user")
def current_user(user: User = f.Depends(find_or_create_user)):
    return f"{user}"


__all__ = (
    "router_auth",
)
