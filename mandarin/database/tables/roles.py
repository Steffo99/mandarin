from __future__ import annotations
from __imports__ import *


class Role(base.Base, a.ColRepr, a.Updatable):
    """
    A role for a person involved with an album or a song.
    """
    __tablename__ = "roles"

    id = s.Column("id", s.Integer, primary_key=True)

    name = s.Column("location", s.String, nullable=False)
    description = s.Column("description", s.Text, nullable=False, default="")

    album_involvements = o.relationship("AlbumInvolvement", back_populates="role", cascade="all, delete")
    song_involvements = o.relationship("SongInvolvement", back_populates="role", cascade="all, delete")

    # noinspection PyTypeChecker
    search = s.Column("search", utils.to_tsvector(
        a=[name],
        b=[description],
    ))

    __table_args__ = (
        utils.gin_index("roles_gin_index", search),
    )


__all__ = (
    "Role",
)
