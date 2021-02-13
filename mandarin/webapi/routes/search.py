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
from ...database import tables

# Special global objects
log = logging.getLogger(__name__)
router_search = f.APIRouter()

SEARCHABLE_ELEMENT_TABLES = {
    models.SearchableElementType.albums: [tables.Album],
    models.SearchableElementType.genres: [tables.Genre],
    models.SearchableElementType.layers: [tables.Layer],
    models.SearchableElementType.people: [tables.Person],
    models.SearchableElementType.roles: [tables.Role],
    models.SearchableElementType.songs: [tables.Song],
    models.SearchableElementType.all: [
        tables.Album,
        tables.Genre,
        tables.Layer,
        tables.Person,
        tables.Role,
        tables.Song
    ]
}

SEARCHABLE_ELEMENT_VECTORS = {
    models.SearchableElementType.albums: tables.Album.search,
    models.SearchableElementType.genres: tables.Genre.search,
    models.SearchableElementType.layers: tables.Layer.search,
    models.SearchableElementType.people: tables.Person.search,
    models.SearchableElementType.roles: tables.Role.search,
    models.SearchableElementType.songs: tables.Song.search,
    models.SearchableElementType.all: (
            tables.Album.search |
            tables.Genre.search |
            tables.Layer.search |
            tables.Person.search |
            tables.Role.search |
            tables.Song.search
    )
}


# Routes
@router_search.get(
    "/autocomplete",
    summary="Prompt possible autocompletitions for a query.",
    response_model=t.List,
    responses={
        **responses.login_error,
    }
)
def search_autocomplete(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        element_type: models.SearchableElementType = f.Query(
            ...,
            description="The type of object that is being searched."
        ),
        query: str = f.Query(..., description="The query that is being written."),
):
    """
    Prompt possible autocompletitions for a query.
    """
    raise NotImplementedError("Not available yet.")


@router_search.get(
    "/results",
    summary="Search for one or more entities in the database.",
    response_model=t.List,
    responses={
        **responses.login_error,
    }
)
def search_results(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        element_type: models.SearchableElementType = f.Query(
            ...,
            description="The type of object that is being retrieved."
        ),
        query: str = f.Query(..., description="The submitted query."),
):
    """
    Search for one or more entities in the database.
    """
    raise NotImplementedError("Not available yet.")


# Objects exported by this module
__all__ = (
    "router_search",
)
