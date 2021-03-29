from __future__ import annotations
from .__imports__ import *

from .songgenres import songgenres
from .albumgenres import albumgenres


class Genre(base.Base, a.ColRepr, a.Updatable):
    """
    A genre of music.
    """
    __tablename__ = "genres"

    id = s.Column("id", s.Integer, primary_key=True)

    name = s.Column("location", s.String, nullable=False, unique=True)
    description = s.Column("description", s.Text, nullable=False, default="")

    supergenre_id = s.Column("supergenre_id", s.Integer, s.ForeignKey("genres.id"), default=0)
    supergenre = o.relationship("Genre", back_populates="subgenres", remote_side=id)
    subgenres = o.relationship("Genre", back_populates="supergenre", remote_side=supergenre_id)

    songs = o.relationship("Song", secondary=songgenres, back_populates="genres")
    albums = o.relationship("Album", secondary=albumgenres, back_populates="genres")

    # noinspection PyTypeChecker
    search = s.Column("search", utils.to_tsvector(
        a=[name],
        b=[description],
    ))

    __table_args__ = (
        utils.gin_index("genres_gin_index", search),
    )


__all__ = (
    "Genre",
)
