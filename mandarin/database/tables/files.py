from __future__ import annotations
from __imports__ import *


class File(base.Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A file that has been uploaded to Mandarin.
    """
    __tablename__ = "files"

    id = s.Column("id", s.Integer, primary_key=True)

    name = s.Column("name", s.String, nullable=False, unique=True)
    mime_type = s.Column("mime_type", s.String)
    mime_software = s.Column("mime_software", s.String)

    uploader_id = s.Column("uploader_id", s.Integer, s.ForeignKey("users.id"))
    uploader = o.relationship("User", back_populates="uploads")

    used_as_layer = o.relationship("Layer", back_populates="file")


__all__ = (
    "File",
)
