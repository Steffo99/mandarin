from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base
from .songgenres import songgenres
from .albumgenres import albumgenres


class MusicGenre(Base, a.ColRepr, a.PyModel):
    """
    A genre of music.
    """
    __tablename__ = "musicgenres"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)

    songs = o.relationship("Song", secondary=songgenres, back_populates="genres")
    albums = o.relationship("Album", secondary=albumgenres, back_populates="genres")

    @classmethod
    def make(cls, session: o.session.Session, name: str) -> MusicGenre:
        """Find the item with the specified name, or create it and add it to the session if it doesn't exist."""
        item = (
            session.query(cls)
                   .filter(a.ieq(cls.name, name))
                   .one_or_none()
        )

        if item is None:
            item = cls(name=name)
            session.add(item)

        return item




__all__ = ("MusicGenre",)
