from __future__ import annotations
from royalnet.typing import *
import fastapi as f

from ...database import *
from ..models import *
from ..dependencies import *

router_debug = f.APIRouter()


@router_debug.patch(
    "/database/reset",
    summary="Drop and recreate all database tables.",
    status_code=204,
    responses={
        **login_error,
    },
)
def database_reset():
    Base.metadata.drop_all()
    Base.metadata.create_all()


__all__ = (
    "router_debug",
)
