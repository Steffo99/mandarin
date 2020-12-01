from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import sqlalchemy.orm.collections as c
import royalnet.alchemist as a

from ..base import Base
from .songgenres import songgenres
from .albumgenres import albumgenres


class Genre(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A genre of music.
    """
    __tablename__ = "genres"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False, unique=True)
    description = s.Column(s.Text, nullable=False, default="")

    supergenre_id = s.Column(s.Integer, s.ForeignKey("genres.id"), server_default="0")
    supergenre = o.relationship("Genre", back_populates="subgenres", remote_side=id)
    subgenres = o.relationship("Genre", back_populates="supergenre", remote_side=supergenre_id)

    songs = o.relationship("Song", secondary=songgenres, back_populates="genres")
    albums = o.relationship("Album", secondary=albumgenres, back_populates="genres")


__all__ = ("Genre",)
