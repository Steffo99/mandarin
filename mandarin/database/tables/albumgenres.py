from royalnet.typing import *
import sqlalchemy as s

from ..base import Base


albumgenres = s.Table(
    "albumgenres", Base.metadata,
    s.Column("_album", s.Integer, s.ForeignKey("albums.id"), primary_key=True),
    s.Column("_genre", s.Integer, s.ForeignKey("genres.id"), primary_key=True)
)
"""
The classification of an album in a certain genre.
"""

__all__ = ("albumgenres",)
