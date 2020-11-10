from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class SongInvolvement(Base, a.ColRepr, a.Updatable):
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

    @classmethod
    def make(cls, session: o.session.Session, **kwargs) -> SongInvolvement:
        """Find the item with the specified values, or create it and add it to the session if it doesn't exist."""
        item = session.query(cls).filter_by(**kwargs).one_or_none()

        if item is None:
            item = cls(**kwargs)
            session.add(item)

        return item

    @classmethod
    def unmake(cls, session: o.session.Session, **kwargs) -> None:
        """Find the item with the specified values, deleting it if it exists and doing nothing otherwise."""
        item = session.query(cls).filter_by(**kwargs).one_or_none()

        if item is not None:
            session.delete(item)


__all__ = ("SongInvolvement",)
