from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class SongLayer(Base, a.ColRepr):
    """
    A single layer of a song.
    """
    __tablename__ = "songlayers"

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False, default="Default", server_default="Default")

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"), nullable=False)
    song = o.relationship("Song", back_populates="layers")

    _file = s.Column(s.Integer, s.ForeignKey("files.id"), nullable=False)
    file = o.relationship("File", back_populates="used_as_songlayer")


__all__ = ("SongLayer",)
