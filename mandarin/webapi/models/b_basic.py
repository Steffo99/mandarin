from royalnet.typing import *
import datetime
import pydantic
from . import a_base as base


class AlbumInvolvement(base.OrmModel):
    person_id: int
    album_id: int
    role_id: int


class Album(base.OrmModel):
    id: int
    title: str
    description: str


class AuditLog(base.OrmModel):
    id: int
    user_id: int
    action: str
    timestamp: datetime.datetime
    obj: int


class File(base.OrmModel):
    id: int
    uploader_id: int


class Genre(base.OrmModel):
    id: int
    name: str
    description: str
    parent_id: Optional[int]


class Layer(base.OrmModel):
    id: int
    name: str
    description: str
    song_id: Optional[int]


class Person(base.OrmModel):
    id: int
    name: str
    description: str


class Role(base.OrmModel):
    id: int
    name: str
    description: str


class SongInvolvement(base.OrmModel):
    person_id: int
    song_id: int
    role_id: int


class Song(base.OrmModel):
    id: int
    title: str
    description: str
    disc: Optional[pydantic.PositiveInt]
    track: Optional[pydantic.PositiveInt]
    year: Optional[int]
    album_id: Optional[int]


class User(base.OrmModel):
    id: int
    sub: str
    name: str
    nickname: str
    picture: str
    email: str
    email_verified: str
    updated_at: str


__all__ = (
    "AlbumInvolvement",
    "Album",
    "AuditLog",
    "File",
    "Genre",
    "Layer",
    "Person",
    "Role",
    "SongInvolvement",
    "Song",
    "User",
)
