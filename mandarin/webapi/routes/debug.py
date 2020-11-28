from __future__ import annotations
from royalnet.typing import *
import fastapi as f

from ...database import tables, Base, engine
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses

router_debug = f.APIRouter()


@router_debug.patch(
    "/database/reset",
    summary="Drop and recreate all database tables.",
    status_code=204,
)
def database_reset():
    """
    **Drop** and **recreate** all tables declared using the `DeclarativeBase` in `mandarin.database.base`.

    **THIS DELETES ALL DATA FROM THE DATABASE!**
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return f.Response(status_code=204)


__all__ = (
    "router_debug",
)
