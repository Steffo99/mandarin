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


PAlbum = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Album)
PSong = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Song)
PLayer = pydantic_sqlalchemy.sqlalchemy_to_pydantic(SongLayer)
PFile = pydantic_sqlalchemy.sqlalchemy_to_pydantic(File)


class PPSong(PSong):
    album: Optional[PAlbum]


class PPLayer(PLayer):
    song: PPSong
    file: Optional[PFile]


class ParseResult(pydantic.BaseModel):
    layer: PPLayer


__all__ = (
    "ParseAlbum",
    "ParseSong",
    "ParseData",
    "ParseResult",
    "PPLayer",
)
