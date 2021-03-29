from __future__ import annotations
from .__imports__ import *


class Encoding(base.Base, a.ColRepr, a.Updatable):
    """
    A music file that has been uploaded to Mandarin.
    """
    __tablename__ = "encodings"

    id = s.Column("id", s.Integer, primary_key=True)

    location = s.Column("location", s.String, nullable=False, unique=True)
    mime_type = s.Column("mime_type", s.String)
    mime_software = s.Column("mime_software", s.String)

    uploader_id = s.Column("uploader_id", s.Integer, s.ForeignKey("users.id"))
    uploader = o.relationship("User", back_populates="uploads")

    layer_id = s.Column("layer_id", s.Integer, s.ForeignKey("layers.id"))
    layer = o.relationship("Layer", back_populates="files")


__all__ = (
    "Encoding",
)
