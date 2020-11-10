from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class Role(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A role for a person involved with an album or a song.
    """
    __tablename__ = "roles"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)
    description = s.Column(s.Text)

    album_involvements = o.relationship("AlbumInvolvement", back_populates="role", cascade="all, delete")
    song_involvements = o.relationship("SongInvolvement", back_populates="role", cascade="all, delete")


__all__ = ("Role",)
