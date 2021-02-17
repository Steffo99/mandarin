"""
Enhanced models are :class:`.OrmModel` that cover various use cases of the data returned by mandarin.
"""

from __future__ import annotations

import pydantic
from royalnet.typing import *

from . import a_base as base
from . import b_basic as basic
from . import c_involvements as involvements
from . import d_inputs as inputs
from . import e_outputs as outputs


class SongFromAlbum(base.OrmModel):
    id: int
    title: str
    description: str
    lyrics: str
    disc: Optional[pydantic.PositiveInt]
    track: Optional[pydantic.PositiveInt]
    year: Optional[int]
    layers: List[basic.Layer]
    involvements: List[involvements.SongInvolvementFromSong]
    genres: List[basic.Genre]


class AlbumWithLayers(base.OrmModel):
    id: int
    title: str
    description: str
    songs: List[SongFromAlbum]
    involvements: List[involvements.AlbumInvolvementFromAlbum]
    genres: List[basic.Genre]


class SongFromGenre(base.OrmModel):
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


class GenreWithLayers(base.OrmModel):
    id: int
    name: str
    description: str
    songs: List[SongFromGenre]
    albums: List[basic.Album]
    supergenre: Optional[basic.Genre]
    subgenres: List[involvements.GenreTree1]


__all__ = (
    "AlbumWithLayers",
    "GenreWithLayers",
)
