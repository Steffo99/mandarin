from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class SongInvolvement(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    The involment of a person in a song.
    """
    __tablename__ = "songinvolvements"

    id = s.Column(s.Integer, primary_key=True)

    _person = s.Column(s.Integer, s.ForeignKey("people.id"))
    person = o.relationship("Person", back_populates="song_involvements")

    _song = s.Column(s.Integer, s.ForeignKey("songs.id"))
    song = o.relationship("Song", back_populates="involvements")

    _role = s.Column(s.Integer, s.ForeignKey("roles.id"))
    role = o.relationship("Role", back_populates="song_involvements")


__all__ = ("SongInvolvement",)
