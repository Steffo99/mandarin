from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class SongInvolvement(Base):
    """
    The involment of a person in a song.
    """
    __tablename__ = "songinvolvements"

    _person = s.Column(s.Integer, s.ForeignKey("people.id"), primary_key=True)
    person = o.relationship("Person", back_populates="song_involvements")

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"), primary_key=True)
    song = o.relationship("Song", back_populates="involvements")

    _role = s.Column(s.Integer, s.ForeignKey("songroles.id"), primary_key=True)
    role = o.relationship("SongRole", back_populates="involvements")


__all__ = ("SongInvolvement",)
