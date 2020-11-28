from royalnet.typing import *
import fastapi as f
import pkg_resources

from ...database import tables
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses


router_version = f.APIRouter()


@router_version.get(
    "/package",
    summary="Get the current version of Mandarin.",
    response_model=Literal[pkg_resources.get_distribution("mandarin").version],
)
def package() -> Literal[pkg_resources.get_distribution("mandarin").version]:
    """
    Return a string representing the [semantic version](https://semver.org/) of the mandarin Python package.
    """
    return pkg_resources.get_distribution("mandarin").version


__all__ = (
    "router_version",
)
