from __future__ import annotations
from __imports__ import *


songgenres = s.Table(
    "songgenres", base.Base.metadata,
    s.Column("song_id", s.Integer, s.ForeignKey("songs.id"), primary_key=True),
    s.Column("genre_id", s.Integer, s.ForeignKey("genres.id"), primary_key=True)
)
"""
The classification of an album in a certain genre.
"""

__all__ = (
    "songgenres",
)
