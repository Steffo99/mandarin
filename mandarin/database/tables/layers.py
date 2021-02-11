import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from mandarin.database.utils import to_tsvector, gin_index
from ..base import Base


class Layer(Base, a.ColRepr, a.Updatable):
    """
    A single layer of a song.
    """
    __tablename__ = "layers"

    id = s.Column("id", s.Integer, primary_key=True)
    name = s.Column("name", s.String, nullable=False, default="Default", server_default="'Default'")
    description = s.Column("description", s.Text, nullable=False, default="")

    song_id = s.Column("song_id", s.Integer, s.ForeignKey("songs.id"))
    song = o.relationship("Song", back_populates="layers")

    file_id = s.Column("file_id", s.Integer, s.ForeignKey("files.id"), nullable=False)
    file = o.relationship("File", back_populates="used_as_layer")

    # noinspection PyTypeChecker
    search = s.Column("search", to_tsvector(
        a=[name],
        b=[description],
    ))

    __table_args__ = (
        gin_index("layers_gin_index", search),
    )


__all__ = ("Layer",)
