"""
This module defines functions useful to add text search support to PostgreSQL database tables.
"""

from __future__ import annotations

import typing as t

import sqlalchemy as s
import sqlalchemy.sql.schema
import sqlalchemy_utils as su


def to_tsvector(
        *,
        a: t.Optional[t.List[s.Column]] = None,
        b: t.Optional[t.List[s.Column]] = None,
        c: t.Optional[t.List[s.Column]] = None,
        d: t.Optional[t.List[s.Column]] = None,
        regconfig: str = "pg_catalog.english"
) -> su.TSVectorType:
    """
    Create a new weighted tsvector type.

    :param a: A :class:`list` of columns that should be in the ``A`` weighting group.
    :param b: A :class:`list` of columns that should be in the ``B`` weighting group.
    :param c: A :class:`list` of columns that should be in the ``C`` weighting group.
    :param d: A :class:`list` of columns that should be in the ``D`` weighting group.
    :param regconfig: The dictionary to use in the tsvector conversion.
    :return: The created :class:`sqlalchemy_utils.TSVectorType`.
    """
    # Set non-mutable args
    if a is None:
        a = []
    if b is None:
        b = []
    if c is None:
        c = []
    if d is None:
        d = []

    column_names = map(lambda column: column.name, [*a, *b, *c, *d])
    column_weights = {
        **{column.name: "A" for column in a},
        **{column.name: "B" for column in b},
        **{column.name: "C" for column in c},
        **{column.name: "D" for column in d},
    }

    return su.TSVectorType(*column_names, weights=column_weights, regconfig=regconfig)


def gin_index(name: str, tsvector: su.TSVectorType) -> s.sql.schema.Index:
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


def gist_index(name: str, tsvector: su.TSVectorType) -> s.sql.schema.Index:
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


__all__ = (
    "to_tsvector",
    "gin_index",
    "gist_index",
)
