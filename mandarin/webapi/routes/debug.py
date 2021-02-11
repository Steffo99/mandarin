from __future__ import annotations

import fastapi as f

from .. import dependencies
from ...database import create_all, Base, lazy_engine

router_debug = f.APIRouter()


@router_debug.patch(
    "/database/reset",
    summary="Drop and recreate all database tables.",
    status_code=204,
)
def database_reset(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
):
    """
    **Drop** and **recreate** all tables declared using the `DeclarativeBase` in `mandarin.database.base`.

    # THIS DELETES ALL DATA FROM THE DATABASE!
    """
    Base.metadata.drop_all(bind=lazy_engine.evaluate())
    create_all()
    return f.Response(status_code=204)


__all__ = (
    "router_debug",
)
