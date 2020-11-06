from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class AlbumRole(Base, a.ColRepr):
    """
    A role for a person involved with an album.
    """
    __tablename__ = "albumroles"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)

    involvements = o.relationship("AlbumInvolvement", back_populates="role")

    @classmethod
    def make(cls, session: o.session.Session, name: str) -> AlbumRole:
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


__all__ = ("AlbumRole",)
