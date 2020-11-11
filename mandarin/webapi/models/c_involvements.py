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


__all__ = (
    "AlbumInvolvementFromPerson",
    "AlbumInvolvementFromRole",
    "AlbumInvolvementFromAlbum",
    "SongInvolvementFromPerson",
    "SongInvolvementFromRole",
    "SongInvolvementFromSong",
)
