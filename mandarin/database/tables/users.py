from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o
import royalnet.alchemist as a

from ..base import Base


class User(Base, a.ColRepr, a.Updatable):
    """
    An user, as returned by OAuth2.
    """
    __tablename__ = "users"

    sub = s.Column(s.String, primary_key=True)
    name = s.Column(s.String, nullable=False)
    nickname = s.Column(s.String, nullable=False)
    picture = s.Column(s.String, nullable=False)
    email = s.Column(s.String, nullable=False)
    email_verified = s.Column(s.String, nullable=False)
    updated_at = s.Column(s.String, nullable=False)

    uploads = o.relationship("File", back_populates="uploader")


__all__ = ("User",)
