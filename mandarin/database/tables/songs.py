from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class Song(Base):
    """
    A single song, composed from multiple layers.
    """
    __tablename__ = "songs"

    id = s.Column(s.Integer, primary_key=True)

    title = s.Column(s.String)

    layers = o.relationship("Layer", back_populates="song")

    _album = s.Column(s.Integer, s.ForeignKey("albums.id"))
    album = o.relationship("Album", back_populates="songs")

    involvements = o.relationship("SongInvolvement", back_populates="songs")
    genres = o.relationship("MusicGenre", secondary="SongGenres", back_populates="songs")

    year = s.Column(s.Integer)


__all__ = ("Song",)
