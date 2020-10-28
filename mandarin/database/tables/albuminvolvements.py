from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class AlbumInvolvement(Base):
    """
    The involment of a person in an album.
    """
    __tablename__ = "albuminvolvements"

    _person = s.Column(s.Integer, s.ForeignKey("people.id"), primary_key=True)
    person = o.relationship("Person", back_populates="song_involvements")

    _album = s.Column(s.Integer, s.ForeignKey("albums.id"), primary_key=True)
    album = o.relationship("Album", back_populates="involvements")

    _role = s.Column(s.Integer, s.ForeignKey("albumroles.id"), primary_key=True)
    role = o.relationship("AlbumRole", back_populates="involvements")


__all__ = ("AlbumInvolvement",)
