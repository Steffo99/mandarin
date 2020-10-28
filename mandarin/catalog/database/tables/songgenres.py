from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class SongGenre(Base):
    """
    The classification of a song in a certain genre.

    As it is a bridge table, it doesn't need any ORM relationships.
    """
    __tablename__ = "songgenres"

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"), primary_key=True)
    _genre = s.Column(s.Integer, s.ForeignKey("musicgenres.id"), primary_key=True)


__all__ = ("SongGenre",)
