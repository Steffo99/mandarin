from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class SongLayer(Base):
    """
    A single layer of a song.
    """
    __tablename__ = "songlayers"

    id = s.Column(s.String, primary_key=True)

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"), nullable=False)
    song = o.relationship("Song", back_populates="layers")


__all__ = ("SongLayer",)
