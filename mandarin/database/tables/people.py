from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class Person(Base):
    """
    A person who is referenced by at least one song in the catalog.
    """
    __tablename__ = "people"

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False)

    song_involvements = o.relationship("SongInvolvement", back_populates="person")
    album_involvements = o.relationship("AlbumInvolvement", back_populates="person")


__all__ = ("Person",)
