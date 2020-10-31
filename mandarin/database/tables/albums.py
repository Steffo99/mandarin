from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base
from .albumgenres import albumgenres


class Album(Base):
    """
    An album, composed of multiple songs.
    """
    __tablename__ = "albums"

    id = s.Column(s.Integer, primary_key=True)
    title = s.Column(s.String, nullable=False)

    involvements = o.relationship("AlbumInvolvement", back_populates="album")

    songs = o.relationship("Song", back_populates="album")
    genres = o.relationship("MusicGenre", secondary=albumgenres, back_populates="albums")


__all__ = ("Album",)
