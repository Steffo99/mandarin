import fastapi as f

from ...database import *
from ..app import *
from ..auth import *


@app.get("/auth/access_token")
def access_token(payload: dict = f.Depends(validate_access_token)):
    return payload


@app.get("/auth/current_user")
def current_user(user: User = f.Depends(find_or_create_user)):
    return f"{user}"


__all__ = (
    "access_token",
    "current_user",
)
