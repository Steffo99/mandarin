from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class AlbumGenre(Base):
    """
    The classification of an album in a certain genre.

    As it is a bridge table, it doesn't need any ORM relationships.
    """
    __tablename__ = "albumgenres"

    _album = s.Column(s.Integer, s.ForeignKey("albums.id"), primary_key=True)
    _genre = s.Column(s.Integer, s.ForeignKey("musicgenres.id"), primary_key=True)


__all__ = ("AlbumGenre",)
