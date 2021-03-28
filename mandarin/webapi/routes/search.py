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
    "albums": tables.Album,
    "genres": tables.Genre,
    "layers": tables.Layer,
    "people": tables.Person,
    "roles": tables.Role,
    "songs": tables.Song,
}

SEARCHABLE_ELEMENT_MODELS = {
    "albums": models.AlbumOutput,
    "genres": models.GenreOutput,
    "layers": models.LayerOutput,
    "people": models.PersonOutput,
    "roles": models.RoleOutput,
    "songs": models.SongOutput,
}


# Routes
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
        query=ls.session.query(SEARCHABLE_ELEMENT_TABLES[element_type]),
        search_query=query,
        sort=True,
        weights=[weight_d, weight_c, weight_b, weight_a],
        normalization=(
            1 if norm_1 else 0 |
            2 if norm_2 else 0 |
            4 if norm_4 else 0 |
            8 if norm_8 else 0 |
            16 if norm_16 else 0 |
            32 if norm_32 else 0
        )
    ).all()
    model = SEARCHABLE_ELEMENT_MODELS[element_type.value]
    if model is None:
        return result
    else:
        return [model.from_orm(obj) for obj in result]


@router_search.get(
    "/thesaurus",
    summary="Search for one or more songs / albums in a certain genre.",
    response_model=list,
    responses={
        **responses.login_error,
    }
)
def search_results(
        ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
        element_type: models.ThesaurusableElementType = f.Query(
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
            description="Divide the rank by 1 + the logarithm of the number of unique words in document."
        ),
        norm_32: bool = f.Query(
            False,
            description="Divide the rank by itself + 1.\n"
                        "\n"
                        "_Shouldn't affect ranking at all._"
        ),
        filter_genre_id: t.Optional[int] = f.Query(
            0,
            description="The id of the genre that queries should be limited to."
        )
):
    """
    Search for one or more songs / albums only in a certain subgenre.
    """
    top = ls.session.query(tables.Genre.id).filter(tables.Genre.id == filter_genre_id).cte("cte", recursive=True)
    bot = ls.session.query(tables.Genre.id).join(top, tables.Genre.supergenre_id == top.c.id)
    genres = top.union(bot)
    element_table = SEARCHABLE_ELEMENT_TABLES[element_type.value]
    elements = ls.session.query(element_table).filter(element_table.genres.any(id=genres.c.id))

    result = ss.search(
        query=elements,
        search_query=query,
        sort=True,
        weights=[weight_d, weight_c, weight_b, weight_a],
        normalization=(
            1 if norm_1 else 0 |
            2 if norm_2 else 0 |
            4 if norm_4 else 0 |
            8 if norm_8 else 0 |
            16 if norm_16 else 0 |
            32 if norm_32 else 0
        )
    ).all()
    model = SEARCHABLE_ELEMENT_MODELS[element_type.value]
    if model is None:
        return result
    else:
        return [model.from_orm(obj) for obj in result]


# Objects exported by this module
__all__ = (
    "router_search",
)
