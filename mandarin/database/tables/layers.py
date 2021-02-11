import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class Layer(Base, a.ColRepr, a.Updatable):
    """
    A single layer of a song.
    """
    __tablename__ = "layers"

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False, default="Default", server_default="'Default'")
    description = s.Column(s.Text, nullable=False, default="")

    song_id = s.Column(s.Integer, s.ForeignKey("songs.id"))
    song = o.relationship("Song", back_populates="layers")

    file_id = s.Column(s.Integer, s.ForeignKey("files.id"), nullable=False)
    file = o.relationship("File", back_populates="used_as_layer")

    __table_args__ = (

    )


__all__ = ("Layer",)
