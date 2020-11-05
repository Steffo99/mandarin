from __future__ import annotations
from royalnet.typing import *
import pydantic
import pydantic_sqlalchemy
import mutagen

from ...database import *


class ParseAlbum(pydantic.BaseModel):
    """Information about the album of a parsed audio file."""
    title: Optional[str]
    artists: List[str]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseAlbum:
        """Create a new Parse object from a mutagen.Tags object."""
        return cls(
            title=ParseData.single(tags=tags, key="album"),
            artists=ParseData.multi(tags=tags, key="albumartists")
        )


class ParseSong(pydantic.BaseModel):
    """Information about the song of a parsed audio file."""
    genre: Optional[str]
    title: Optional[str]
    year: Optional[int]
    disc_number: Optional[int]
    track_number: Optional[int]
    artists: List[str]
    composers: List[str]
    performers: List[str]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseSong:
        """Create a new Parse object from a mutagen.Tags object."""
        return cls(
            genre=ParseData.single(tags=tags, key="genre"),
            title=ParseData.single(tags=tags, key="title"),
            year=ParseData.integer(tags=tags, key="date"),
            disc_number=ParseData.integer(tags=tags, key="discnumber"),
            track_number=ParseData.integer(tags=tags, key="tracknumber"),
            artists=ParseData.multi(tags=tags, key="artist"),
            composers=ParseData.multi(tags=tags, key="composer"),
            performers=ParseData.multi(tags=tags, key="performer"),
        )


class ParseData(pydantic.BaseModel):
    """Information about a parsed audio file."""
    album: ParseAlbum
    song: ParseSong

    @staticmethod
    def single(tags: mutagen.Tags, key: str, default: Any = None) -> Any:
        """Get the full value contained inside a specific tag."""
        value = tags.get(key)

        if value is None:
            return default

        if len(value) == 0:
            return default

        return value[0].strip()

    @staticmethod
    def integer(tags: mutagen.Tags, key: str, default: Any = None, error: Any = None) -> Any:
        """Get the full value contained inside a specific tag, as int"""
        value = ParseData.single(tags=tags, key=key)

        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            return error

    @staticmethod
    def multi(tags: mutagen.Tags, key: str) -> List[str]:
        """Get all the values (slash-separated) contained inside a specific tag."""
        value = ParseData.single(tags=tags, key=key)

        if value is None:
            return []

        if value == "":
            return []

        else:
            return [item.strip() for item in value.split("/")]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseData:
        return ParseData(
            album=ParseAlbum.from_tags(tags),
            song=ParseSong.from_tags(tags),
        )


class UploadFile(pydantic_sqlalchemy.sqlalchemy_to_pydantic(File)):
    """Information about the file that was uploaded and stored in Mandarin."""


class UploadPerson(pydantic_sqlalchemy.sqlalchemy_to_pydantic(Person)):
    """A person that was involved with the uploaded song or album."""


class UploadGenre(pydantic_sqlalchemy.sqlalchemy_to_pydantic(MusicGenre)):
    """The music genre of the uploaded song or album."""


class UploadSongRole(pydantic_sqlalchemy.sqlalchemy_to_pydantic(SongRole)):
    """The role with which a person was involved with the uploaded song."""


class UploadAlbumRole(pydantic_sqlalchemy.sqlalchemy_to_pydantic(AlbumRole)):
    """The role with which a person was involved with the uploaded album."""


class UploadAlbumInvolvement(pydantic_sqlalchemy.sqlalchemy_to_pydantic(AlbumInvolvement)):
    """The involvement of a specific person, having a role ("Artist"), with the uploaded album."""
    person: UploadPerson
    role: UploadAlbumRole


class UploadAlbum(pydantic_sqlalchemy.sqlalchemy_to_pydantic(Album)):
    """The album that was created during the upload, or that was associated with the new layer."""
    genres: List[UploadGenre]
    involvements: List[UploadAlbumInvolvement]


class UploadSongInvolvement(pydantic_sqlalchemy.sqlalchemy_to_pydantic(SongInvolvement)):
    """The involvement of a specific person, having a role ("Artist"), with the uploaded song."""
    person: UploadPerson
    role: UploadSongRole


class UploadSong(pydantic_sqlalchemy.sqlalchemy_to_pydantic(Song)):
    """The song that was created during the upload, or that was associated with the new layer."""
    album: Optional[UploadAlbum]
    involvements: List[UploadSongInvolvement]
    genres: List[UploadGenre]


class UploadLayer(pydantic_sqlalchemy.sqlalchemy_to_pydantic(SongLayer)):
    """The layer that was created during the upload."""
    song: UploadSong
    file: Optional[UploadFile]


class UploadResult(pydantic.BaseModel):
    """The result of the upload of a track to Mandarin."""
    layer: UploadLayer


__all__ = (
    "ParseAlbum",
    "ParseSong",
    "ParseData",
    "UploadFile",
    "UploadPerson",
    "UploadGenre",
    "UploadSongRole",
    "UploadAlbumRole",
    "UploadAlbumInvolvement",
    "UploadAlbum",
    "UploadSongInvolvement",
    "UploadSong",
    "UploadLayer",
    "UploadResult",
)
