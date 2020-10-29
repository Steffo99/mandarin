from royalnet.typing import *
import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class User(Base):
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


__all__ = ("User",)
