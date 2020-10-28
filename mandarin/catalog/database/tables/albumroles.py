from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class AlbumRole(Base):
    """
    A role for a person involved with an album.
    """
    __tablename__ = "albumroles"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)

    involvements = o.relationship("AlbumInvolvements", back_populates="role")


__all__ = ("AlbumRole",)
