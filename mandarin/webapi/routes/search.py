# Module docstring
"""
This module contains a router with full-text-search related methods.
"""

# Special imports
from __future__ import annotations

import logging
import typing as t

# External imports
import fastapi as f

# Internal imports
from .. import dependencies
from .. import models
from .. import responses

# Special global objects
log = logging.getLogger(__name__)
router_search = f.APIRouter()


# Routes
@router_search.get(
    "/songs",
    summary="Search for one or more songs.",
    response_model=t.List[models.SongOutput],
    responses={
        **responses.login_error,
    }
)
def search_songs(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        query: str = f.Query(..., description="The query to pass to the search engine.")
):
    """
    Search for one or more songs using Mandarin's PostgreSQL-based search engine.

    _Doesn't do anything yet._
    """
    raise NotImplementedError("Not available yet.")


@router_search.get(
    "/people",
    summary="Search for one or more people.",
    response_model=t.List[models.PersonOutput],
    responses={
        **responses.login_error,
    }
)
def search_people(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        query: str = f.Query(..., description="The query to pass to the search engine.")
):
    """
    Search for one or more people using Mandarin's PostgreSQL-based search engine.

    _Doesn't do anything yet._
    """
    raise NotImplementedError("Not available yet.")


@router_search.get(
    "/albums",
    summary="Search for one or more albums.",
    response_model=t.List[models.PersonOutput],
    responses={
        **responses.login_error,
    }
)
def search_albums(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        query: str = f.Query(..., description="The query to pass to the search engine.")
):
    """
    Search for one or more albums using Mandarin's PostgreSQL-based search engine.

    _Doesn't do anything yet._
    """
    raise NotImplementedError("Not available yet.")


# Objects exported by this module
__all__ = (
    "router_search",
)
