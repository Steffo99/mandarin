import fastapi as f
import pkg_resources


router_version = f.APIRouter()


@router_version.get(
    "/package",
    summary="Get the current version of Mandarin.",
    response_model=str,
)
def package():
    return pkg_resources.get_distribution("mandarin").version


__all__ = (
    "router_version",
)
