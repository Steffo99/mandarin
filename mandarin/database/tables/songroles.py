from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class SongRole(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A role for a person involved with a song.
    """
    __tablename__ = "songroles"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)
    description = s.Column(s.Text)

    involvements = o.relationship("SongInvolvement", back_populates="role", cascade="all, delete")


__all__ = ("SongRole",)
