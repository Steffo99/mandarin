"""
Involvement models are :class:`.OrmModel` that represent **junction tables** or parts of **autoassociations** (which
cannot be represented properly through :mod:`pydantic`).
"""

from royalnet.typing import *
from . import a_base as base
from . import b_basic as basic


class AlbumInvolvementFromPerson(base.OrmModel):
    album: basic.Album
    role: basic.Role


class AlbumInvolvementFromRole(base.OrmModel):
    person: basic.Person
    album: basic.Album


class AlbumInvolvementFromAlbum(base.OrmModel):
    person: basic.Person
    role: basic.Role


class SongInvolvementFromPerson(base.OrmModel):
    song: basic.Song
    role: basic.Role


class SongInvolvementFromRole(base.OrmModel):
    person: basic.Person
    song: basic.Song


class SongInvolvementFromSong(base.OrmModel):
    person: basic.Person
    role: basic.Role


class GenreTree1(base.OrmModel):
    id: int
    name: str
    description: str
    subgenres: List


class GenreTree2(base.OrmModel):
    id: int
    name: str
    description: str
    subgenres: List[GenreTree1]


__all__ = (
    "AlbumInvolvementFromPerson",
    "AlbumInvolvementFromRole",
    "AlbumInvolvementFromAlbum",
    "SongInvolvementFromPerson",
    "SongInvolvementFromRole",
    "SongInvolvementFromSong",
    "GenreTree1",
    "GenreTree2",
)
