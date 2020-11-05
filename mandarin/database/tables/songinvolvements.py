from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class SongInvolvement(Base, a.ColRepr, a.PyModel):
    """
    The involment of a person in a song.
    """
    __tablename__ = "songinvolvements"

    id = s.Column(s.Integer, primary_key=True)

    _person = s.Column(s.Integer, s.ForeignKey("people.id"))
    person = o.relationship("Person", back_populates="song_involvements")

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"))
    song = o.relationship("Song", back_populates="involvements")

    _role = s.Column(s.Integer, s.ForeignKey("songroles.id"))
    role = o.relationship("SongRole", back_populates="involvements")


__all__ = ("SongInvolvement",)
