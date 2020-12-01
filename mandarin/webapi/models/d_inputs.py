from royalnet.typing import *
import datetime
import pydantic
from . import a_base as base


class AlbumInvolvementInput(base.OrmModel):
    person_id: int
    album_id: int
    role_id: int


class AlbumInput(base.OrmModel):
    title: str
    description: str


class AuditLogInput(base.OrmModel):
    user_id: int
    action: str
    timestamp: datetime.datetime
    obj: int


class FileInput(base.OrmModel):
    uploader_id: int


class GenreInput(base.OrmModel):
    name: str
    description: str
    parent_id: Optional[int]


class LayerInput(base.OrmModel):
    name: str
    description: str
    song_id: Optional[int]


class PersonInput(base.OrmModel):
    name: str
    description: str


class RoleInput(base.OrmModel):
    name: str
    description: str


class SongInvolvementInput(base.OrmModel):
    person_id: int
    song_id: int
    role_id: int


class SongInput(base.OrmModel):
    title: str
    description: str
    disc: Optional[pydantic.PositiveInt]
    track: Optional[pydantic.PositiveInt]
    year: Optional[int]
    album_id: Optional[int]


__all__ = (
    "AlbumInvolvementInput",
    "AlbumInput",
    "AuditLogInput",
    "FileInput",
    "GenreInput",
    "LayerInput",
    "PersonInput",
    "RoleInput",
    "SongInvolvementInput",
    "SongInput",
)
