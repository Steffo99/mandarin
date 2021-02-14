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
import sqlalchemy_searchable as ss

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

SEARCHABLE_ELEMENT_MODELS: t.Dict[models.SearchableElementType, t.Optional[models.OrmModel]] = {
    models.SearchableElementType.albums: models.AlbumOutput,
    models.SearchableElementType.genres: models.GenreOutput,
    models.SearchableElementType.layers: models.LayerOutput,
    models.SearchableElementType.people: models.PersonOutput,
    models.SearchableElementType.roles: models.RoleOutput,
    models.SearchableElementType.songs: models.SongOutput,
    models.SearchableElementType.all: None
}


# Routes
@router_search.get(
    "/autocomplete",
    summary="Prompt possible autocompletitions for a query.",
    response_model=list,
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
    response_model=list,
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
        weight_d: float = f.Query(
            0.1,
            description="The weight that D-tagged tokens should have.\n"
                        "\n"
                        "_Currently, nothing is tagged with D._"
        ),
        weight_c: float = f.Query(
            0.2,
            description="The weight that C-tagged tokens should have.\n"
                        "\n"
                        "Usually, **lyrics** are tagged with C."
        ),
        weight_b: float = f.Query(
            0.4,
            description="The weight that B-tagged tokens should have.\n"
                        "\n"
                        "Usually, **descriptions** are tagged with B."
        ),
        weight_a: float = f.Query(
            1.0,
            description="The weight that A-tagged tokens should have.\n"
                        "\n"
                        "Usually, **titles** and **names** are tagged with A."
        ),
        norm_1: bool = f.Query(
            False,
            description="Divide the rank by 1 + the logarithm of the document length."
        ),
        norm_2: bool = f.Query(
            False,
            description="Divide the rank by the document length."
        ),
        norm_4: bool = f.Query(
            False,
            description="Divide the rank by the mean harmonic distance between extents."
        ),
        norm_8: bool = f.Query(
            False,
            description="Divide the rank by the number of unique words in document."
        ),
        norm_16: bool = f.Query(
            False,
            description="Divide the rank by 1 + the logarithm of the number of unique words in document"
        ),
        norm_32: bool = f.Query(
            False,
            description="Divide the rank by itself + 1.\n"
                        "\n"
                        "_Shouldn't affect ranking at all._"
        ),
):
    """
    Search for one or more entities in the database.
    """
    result = ss.search(
        query=ls.session.query(*SEARCHABLE_ELEMENT_TABLES[element_type]),
        search_query=query,
        weights=(weight_d, weight_c, weight_b, weight_a),
        normalization=(
            1 if norm_1 else 0 |
            2 if norm_2 else 0 |
            4 if norm_4 else 0 |
            8 if norm_8 else 0 |
            16 if norm_16 else 0 |
            32 if norm_32 else 0
        )
    ).all()
    model = SEARCHABLE_ELEMENT_MODELS[element_type]
    if model is None:
        return result
    else:
        return [model.from_orm(obj) for obj in result]


# Objects exported by this module
__all__ = (
    "router_search",
)
