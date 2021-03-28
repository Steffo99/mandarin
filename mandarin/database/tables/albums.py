from __future__ import annotations
from __imports__ import *

from .albumgenres import albumgenres

if t.TYPE_CHECKING:
    from .albuminvolvements import AlbumInvolvement


class Album(base.Base, a.ColRepr, a.Updatable):
    """
    An album, composed of multiple songs.
    """
    __tablename__ = "albums"

    id = s.Column("id", s.Integer, primary_key=True)
    title = s.Column("title", s.String, nullable=False, default="")
    description = s.Column("description", s.Text, nullable=False, default="")

    involvements: list["AlbumInvolvement"] = o.relationship("AlbumInvolvement", back_populates="album")
    songs = o.relationship("Song", back_populates="album")
    genres = o.relationship("Genre", secondary=albumgenres, back_populates="albums")

    # noinspection PyTypeChecker
    search = s.Column("search", utils.to_tsvector(
        a=[title],
        b=[description],
    ))

    __table_args__ = (
        utils.gin_index("albums_gin_index", search),
    )


__all__ = (
    "Album",
)
