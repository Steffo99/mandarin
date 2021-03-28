from __future__ import annotations

import dataclasses
import logging

from royalnet.typing import *

log = logging.getLogger(__name__)


@dataclasses.dataclass()
class MutagenParse:
    """
    A sanitizer and container class for data returned in the :class:`mutagen.Tags` format.
    """

    @dataclasses.dataclass()
    class Album:
        title: Optional[str]
        artists: List[str]

        @classmethod
        def from_tags(cls, tag: Dict[str, List[str]]) -> MutagenParse.Album:
            return cls(
                title=MutagenParse.single_string(tag=tag, key="album"),
                artists=MutagenParse.multi_string(tag=tag, key="albumartist")
            )

    @dataclasses.dataclass()
    class Song:
        genre: Optional[str]
        title: Optional[str]
        year: Optional[int]
        disc_number: Optional[int]
        track_number: Optional[int]
        artists: List[str]
        composers: List[str]
        performers: List[str]

        @classmethod
        def from_tags(cls, tag: Dict[str, List[str]]) -> MutagenParse.Song:
            return cls(
                genre=MutagenParse.single_string(tag=tag, key="genre"),
                title=MutagenParse.single_string(tag=tag, key="title"),
                year=MutagenParse.single_integer(tag=tag, key="date"),
                disc_number=MutagenParse.single_integer(tag=tag, key="discnumber"),
                track_number=MutagenParse.single_integer(tag=tag, key="tracknumber"),
                artists=MutagenParse.multi_string(tag=tag, key="artist"),
                composers=MutagenParse.multi_string(tag=tag, key="composer"),
                performers=MutagenParse.multi_string(tag=tag, key="performer"),
            )

    album: Album
    song: Song

    @staticmethod
    def single_string(tag: Dict[str, List[str]], key: str, default: Any = None) -> Any:
        log.debug(f"Accessing {key} tag as single string...")

        values = tag.get(key)
        if values is None:
            log.debug(f"No such tag, returning {default}")
            return default
        if len(values) == 0:
            log.debug(f"Tag is empty, returning {default}")
            return default
        elif len(values) > 1:
            log.debug(f"Multiple tags available for {key}, keeping the first and discarding the rest")

        log.debug(f"Read {values[0]}, stripping garbage")
        result = values[0].strip()

        log.debug(f"{key} tag successfully parsed as {result}")
        return result

    @staticmethod
    def single_integer(tag: Dict[str, List[str]], key: str, default: Any = None, error: Any = None) -> Any:
        log.debug(f"Accessing {key} tag as single integer...")

        value = tag.get(key)
        if value is None:
            log.debug(f"No such tag, returning {default}")
            return default
        if len(value) == 0:
            log.debug(f"Tag is empty, returning {default}")
            return default
        elif len(value) > 1:
            log.debug(f"Multiple tags available for {key}, keeping the first and discarding the rest")

        log.debug(f"Read {value[0]}, stripping garbage")
        string = value[0].strip()

        try:
            log.debug(f"Casting {string} to integer")
            result = int(string)
        except ValueError:
            log.debug(f"Couldn't cast {string} to integer, returning {error}")
            return error
        else:
            log.debug(f"{key} tag successfully parsed as {result}")
            return result

    @staticmethod
    def multi_string(tag: Dict[str, List[str]], key: str) -> List[str]:
        log.debug(f"Accessing {key} tag as multiple string...")

        values = tag.get(key)

        if values is None:
            log.debug(f"No such tag, returning an empty list")
            return []

        log.debug(f"Read {values[0]}, splitting slashes")

        result = []
        for value in values:
            split = value.split("/")
            for s in split:
                result.append(s.strip())

        log.debug(f"{key} tag successfully parsed as {result}")
        return result

    @classmethod
    def from_tags(cls, tag: Dict[str, List[str]]) -> MutagenParse:
        return MutagenParse(
            album=MutagenParse.Album.from_tags(tag),
            song=MutagenParse.Song.from_tags(tag),
        )


__all__ = (
    "MutagenParse",
)
