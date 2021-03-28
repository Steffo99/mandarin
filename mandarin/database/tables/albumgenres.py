from __future__ import annotations
from __imports__ import *


albumgenres = s.Table(
    "albumgenres", base.Base.metadata,
    s.Column("album_id", s.Integer, s.ForeignKey("albums.id"), primary_key=True),
    s.Column("genre_id", s.Integer, s.ForeignKey("genres.id"), primary_key=True)
)
"""
The classification of an album in a certain genre.
"""

__all__ = (
    "albumgenres",
)
