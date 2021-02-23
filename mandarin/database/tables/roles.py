import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from mandarin.database.utils import to_tsvector, gin_index
from ..base import Base


class Role(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A role for a person involved with an album or a song.
    """
    __tablename__ = "roles"

    id = s.Column("id", s.Integer, primary_key=True)

    name = s.Column("name", s.String, nullable=False)
    description = s.Column("description", s.Text, nullable=False, default="")

    album_involvements = o.relationship("AlbumInvolvement", back_populates="role", cascade="all, delete-orphan")
    song_involvements = o.relationship("SongInvolvement", back_populates="role", cascade="all, delete-orphan")

    # noinspection PyTypeChecker
    search = s.Column("search", to_tsvector(
        a=[name],
        b=[description],
    ))

    __table_args__ = (
        gin_index("roles_gin_index", search),
    )


__all__ = ("Role",)
