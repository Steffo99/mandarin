from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class MusicGenre(Base):
    """
    A genre of music.
    """
    __tablename__ = "musicgenres"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)

    songs = o.relationship("Song", secondary="SongGenre", back_populates="genres")
    albums = o.relationship("Album", secondary="AlbumGenre", back_populates="genres")


__all__ = ("MusicGenre",)
