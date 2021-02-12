"""
Extra models are :class:`.MandarinModel`\\ s which represent data not contained in the database.
"""

import enum

from . import a_base as base


class AuthConfig(base.MandarinModel):
    authorization: str
    device: str
    token: str
    refresh: str
    userinfo: str
    openidcfg: str
    jwks: str


class SearchableElementType(str, enum.Enum):
    albums = "albums"
    genres = "genres"
    layers = "layers"
    people = "people"
    roles = "roles"
    songs = "songs"
    all = "all"


__all__ = (
    "AuthConfig",
    "SearchableElementType",
)
