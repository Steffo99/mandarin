# Module docstring
"""
This module defines functions useful to add text search support to PostgreSQL database tables.
"""

# Special imports
from __future__ import annotations

# External imports
import logging
import typing as t
from functools import reduce

import sqlalchemy as s
import sqlalchemy.sql.operators as so

# Internal imports
# from . import something

# Special global objects
log = logging.getLogger(__name__)


# Code
# noinspection PyPep8Naming
def to_tsvector(a: t.List, b: t.List, c: t.List, d: t.List, *, language: str = "english"):
    """
    Create a new weighted tsvector.

    :param a: A :class:`list` of columns that should be in the ``A`` weighting group.
    :param b: A :class:`list` of columns that should be in the ``B`` weighting group.
    :param c: A :class:`list` of columns that should be in the ``C`` weighting group.
    :param d: A :class:`list` of columns that should be in the ``D`` weighting group.
    :param language: The language to use in the tsvector conversion.
    :return: The created tsvector.
    """
    # Coalesce null strings
    a = map(lambda column: s.func.coalesce(column, ""), a)
    b = map(lambda column: s.func.coalesce(column, ""), b)
    c = map(lambda column: s.func.coalesce(column, ""), c)
    d = map(lambda column: s.func.coalesce(column, ""), d)

    # Convert everything to tsvectors
    a = map(lambda column: s.func.to_tsvector(language, column), a)
    b = map(lambda column: s.func.to_tsvector(language, column), b)
    c = map(lambda column: s.func.to_tsvector(language, column), c)
    d = map(lambda column: s.func.to_tsvector(language, column), d)

    # Assign weight to the tsvectors
    a = map(lambda vec: s.func.setweight(vec, "A"), a)
    b = map(lambda vec: s.func.setweight(vec, "B"), b)
    c = map(lambda vec: s.func.setweight(vec, "C"), c)
    d = map(lambda vec: s.func.setweight(vec, "D"), d)

    # Concatenate all weighted tsvectors
    return reduce(lambda x, y: so.op(x, "||", y), [*a, *b, *c, *d])


def gin_index(name, tsvector):
    """
    Create a new GIN index.

    :param name: The name of the index.
    :param tsvector: The tsvector to use for the index.
    :return: The Index object.
    """
    return s.Index(
        name,
        tsvector,
        postgresql_using="GIN"
    )


def gist_index(name, tsvector):
    """
    Create a new GiST index.

    :param name: The name of the index.
    :param tsvector: The tsvector to use for the index.
    :return: The Index object.
    """
    return s.Index(
        name,
        tsvector,
        postgresql_using="GIST"
    )


# Objects exported by this module
__all__ = (
    "to_tsvector",
    "gin_index",
    "gist_index",
)
