from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class Album(Base):
    """
    An album, composed of multiple songs.
    """
    __tablename__ = "albums"

    id = s.Column(s.Integer, primary_key=True)

    involvements = o.relationship("AlbumInvolvements", back_populates="album")

    songs = o.relationship("Song", back_populates="album")
    genres = o.relationship("MusicGenre", secondary="AlbumGenres", back_populates="albums")


__all__ = ("Album",)
