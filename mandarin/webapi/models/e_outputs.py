"""
Output models are :class:`.OrmModel` that represent the **full data** of database tables.

In them, :func:`sqlalchemy.orm.relationship` should be expanded up to 1 layer, and then regular :mod:`.b_basic`
objects should be used.

They are returned by most methods of the API.
"""

from __future__ import annotations

import datetime

import pydantic
from royalnet.typing import *

from . import a_base as base
from . import b_basic as basic
from . import c_involvements as involvements


class AlbumInvolvementOutput(base.OrmModel):
    person: basic.Person
    album: basic.Album
    role: basic.Role


class AlbumOutput(base.OrmModel):
    id: int
    title: str
    description: str
    songs: List[basic.Song]
    involvements: List[involvements.AlbumInvolvementFromAlbum]
    genres: List[basic.Genre]


class AuditLogOutput(base.OrmModel):
    id: int
    user: basic.User
    action: str
    timestamp: datetime.datetime
    obj: int


class FileOutput(base.OrmModel):
    id: int
    uploader: basic.User


class GenreOutput(base.OrmModel):
    id: int
    name: str
    description: str
    songs: List[basic.Song]
    albums: List[basic.Album]
    supergenre: Optional[basic.Genre]
    subgenres: List[basic.Genre]


class GenreTreeOutput(base.OrmModel):
    id: int
    name: str
    description: str
    subgenres: List[involvements.GenreTree2]


class LayerOutput(base.OrmModel):
    id: int
    name: str
    description: str
    song: Optional[basic.Song]


class PersonOutput(base.OrmModel):
    id: int
    name: str
    description: str
    song_involvements: List[involvements.SongInvolvementFromPerson]
    album_involvements: List[involvements.AlbumInvolvementFromPerson]


class RoleOutput(base.OrmModel):
    id: int
    name: str
    description: str
    song_involvements: List[involvements.SongInvolvementFromRole]
    album_involvements: List[involvements.AlbumInvolvementFromRole]


class SongInvolvementOutput(base.OrmModel):
    person: basic.Person
    song: basic.Song
    role: basic.Role


class SongOutput(base.OrmModel):
    id: int
    title: str
    description: str
    lyrics: str
    disc: Optional[pydantic.PositiveInt]
    track: Optional[pydantic.PositiveInt]
    year: Optional[int]
    album: Optional[basic.Album]
    layers: List[basic.Layer]
    involvements: List[involvements.SongInvolvementFromSong]
    genres: List[basic.Genre]


class UserOutput(base.OrmModel):
    id: int
    sub: str
    name: str
    nickname: str
    picture: str
    email: str
    email_verified: str
    updated_at: str
    audit_logs: List[basic.AuditLog]


__all__ = (
    "AlbumInvolvementOutput",
    "AlbumOutput",
    "AuditLogOutput",
    "FileOutput",
    "GenreOutput",
    "GenreTreeOutput",
    "LayerOutput",
    "PersonOutput",
    "RoleOutput",
    "SongInvolvementOutput",
    "SongOutput",
    "UserOutput",
)
