from __future__ import annotations
from .__imports__ import *

from .songgenres import songgenres

if t.TYPE_CHECKING:
    from .songinvolvements import SongInvolvement


class Song(base.Base, a.ColRepr, a.Updatable):
    """
    A single song, composed from multiple layers.
    """
    __tablename__ = "songs"

    id = s.Column("id", s.Integer, primary_key=True)

    title = s.Column("title", s.String, nullable=False, default="")
    description = s.Column("description", s.Text, nullable=False, default="")
    lyrics = s.Column("lyrics", s.Text, nullable=False, default="")

    disc = s.Column("disc", s.Integer)
    track = s.Column("track", s.Integer)
    year = s.Column("year", s.Integer)

    album_id = s.Column("album_id", s.Integer, s.ForeignKey("albums.id"))
    album = o.relationship("Album", back_populates="songs")

    layers = o.relationship("Layer", back_populates="song")
    involvements: list["SongInvolvement"] = o.relationship("SongInvolvement", back_populates="song",
                                                           cascade="all, delete")
    genres = o.relationship("Genre", secondary=songgenres, back_populates="songs")

    # noinspection PyTypeChecker
    search = s.Column("search", utils.to_tsvector(
        a=[title],
        b=[description],
        c=[lyrics],
    ))

    __table_args__ = (

    )


__all__ = ("Song",)
