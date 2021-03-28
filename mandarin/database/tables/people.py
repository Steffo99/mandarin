from __future__ import annotations
from __imports__ import *


class Person(base.Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A person who is referenced by at least one song in the catalog.
    """
    __tablename__ = "people"

    id = s.Column("id", s.Integer, primary_key=True)
    name = s.Column("name", s.String, nullable=False)
    description = s.Column("description", s.Text, nullable=False, default="")

    song_involvements = o.relationship("SongInvolvement", back_populates="person", cascade="all, delete")
    album_involvements = o.relationship("AlbumInvolvement", back_populates="person", cascade="all, delete")

    # noinspection PyTypeChecker
    search = s.Column("search", utils.to_tsvector(
        a=[name],
        b=[description],
    ))

    __table_args__ = (
        utils.gin_index("people_gin_index", search),
    )


__all__ = (
    "Person",
)
