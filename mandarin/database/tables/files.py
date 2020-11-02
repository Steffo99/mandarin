from __future__ import annotations
from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import mimetypes

from ..base import Base

if TYPE_CHECKING:
    from .users import User


class File(Base):
    """
    A file that has been uploaded to Mandarin.
    """
    __tablename__ = "files"

    id = s.Column(s.Integer, primary_key=True)

    name = s.Column(s.String, nullable=False)
    mime_type = s.Column(s.String)

    _uploader = s.Column(s.String, s.ForeignKey("users.sub"))
    uploader = o.relationship("User", back_populates="uploads")

    @classmethod
    def guess(cls, name: str, uploader: User) -> File:
        return cls(name=name, mime_type=mimetypes.guess_type(name, strict=False), uploader=uploader)


__all__ = (File,)