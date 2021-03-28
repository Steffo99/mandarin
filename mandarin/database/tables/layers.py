from __future__ import annotations
from __imports__ import *


class Layer(base.Base, a.ColRepr, a.Updatable):
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
    search = s.Column("search", utils.to_tsvector(
        a=[name],
        b=[description],
    ))

    __table_args__ = (
        utils.gin_index("layers_gin_index", search),
    )


__all__ = ("Layer",)
