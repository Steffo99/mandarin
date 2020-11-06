from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a
import mimetypes

from ..base import Base

if TYPE_CHECKING:
    from .users import User


class File(Base, a.ColRepr):
    """
    A file that has been uploaded to Mandarin.
    """
    __tablename__ = "files"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)
    mime_type = s.Column(s.String)
    mime_software = s.Column(s.String)

    _uploader = s.Column(s.String, s.ForeignKey("users.sub"))
    uploader = o.relationship("User", back_populates="uploads")

    used_as_layer = o.relationship("Layer", back_populates="file")
    used_as_album_cover = o.relationship("Album", back_populates="cover")

    @classmethod
    def make(cls, session: o.session.Session, name: str, uploader: Optional[User] = None) -> File:
        """Find the item with the specified name, or create it and add it to the session if it doesn't exist."""
        item = (
            session.query(cls)
                   .filter(cls.name == name)
                   .one_or_none()
        )

        if item is None:
            item = cls(name=name, uploader=uploader)
            session.add(item)

        return item

    @classmethod
    def guess(cls, name: str, uploader: Optional[User] = None) -> File:
        mtype, msoftware = mimetypes.guess_type(name, strict=False)
        return cls(name=name, mime_type=mtype, mime_software=msoftware, uploader=uploader)


__all__ = ("File",)
