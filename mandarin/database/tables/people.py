from __future__ import annotations

import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base
from mandarin.database.utils import to_tsvector

class Person(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A person who is referenced by at least one song in the catalog.
    """
    __tablename__ = "people"

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False)
    description = s.Column(s.Text, nullable=False, default="")

    song_involvements = o.relationship("SongInvolvement", back_populates="person", cascade="all, delete")
    album_involvements = o.relationship("AlbumInvolvement", back_populates="person", cascade="all, delete")

    __table_args__ = (
        to_tsvector(
            a=[name],
            b=[description],
        )
    )


__all__ = ("Person",)
