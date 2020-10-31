from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class SongLayer(Base):
    """
    A single layer of a song.
    """
    __tablename__ = "songlayers"

    id = s.Column(s.Integer, primary_key=True)

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"), nullable=False)
    song = o.relationship("Song", back_populates="layers")

    _uploader = s.Column(s.String, s.ForeignKey("users.sub"))
    uploader = o.relationship("User", back_populates="uploads")

    filename = s.Column(s.String)


__all__ = ("SongLayer",)
