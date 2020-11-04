import fastapi as f

from ...database import *
from ..utils.auth import *


router_metadata = f.APIRouter()


@router_metadata.get("/", summary="PLACEHOLDER")
def y():
    pass


__all__ = (
    "router_metadata",
)
