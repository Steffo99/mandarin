from royalnet.typing import *
import sqlalchemy as s

from ..base import Base


songgenres = s.Table(
    "songgenres", Base.metadata,
    s.Column("_song", s.Integer, s.ForeignKey("songs.id"), primary_key=True),
    s.Column("_genre", s.Integer, s.ForeignKey("genres.id"), primary_key=True)
)
"""
The classification of an album in a certain genre.
"""

__all__ = ("songgenres",)
