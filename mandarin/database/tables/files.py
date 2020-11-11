from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a
import mimetypes

from ..base import Base


class File(Base, a.ColRepr, a.Updatable, a.Makeable):
    """
    A file that has been uploaded to Mandarin.
    """
    __tablename__ = "files"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False, unique=True)
    mime_type = s.Column(s.String)
    mime_software = s.Column(s.String)

    uploader_id = s.Column(s.Integer, s.ForeignKey("users.id"))
    uploader = o.relationship("User", back_populates="uploads")

    used_as_layer = o.relationship("Layer", back_populates="file")

    @classmethod
    def guess(cls, name: str, *, session: o.session.Session, **kwargs) -> File:
        mtype, msoftware = mimetypes.guess_type(name, strict=False)
        return cls.make(session=session, name=name, mime_type=mtype, mime_software=msoftware, **kwargs)


__all__ = ("File",)
