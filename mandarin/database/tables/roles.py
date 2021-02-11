import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class Role(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A role for a person involved with an album or a song.
    """
    __tablename__ = "roles"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)
    description = s.Column(s.Text, nullable=False, default="")

    album_involvements = o.relationship("AlbumInvolvement", back_populates="role", cascade="all, delete")
    song_involvements = o.relationship("SongInvolvement", back_populates="role", cascade="all, delete")

    __table_args__ = (

    )


__all__ = ("Role",)
