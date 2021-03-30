from __future__ import annotations
from .__imports__ import *


class User(base.Base, a.ColRepr, a.Updatable):
    """
    An user, as returned by OAuth2.
    """
    __tablename__ = "users"

    id = s.Column("id", s.Integer, primary_key=True)

    sub = s.Column("sub", s.String, nullable=False)
    name = s.Column("name", s.String, nullable=False)
    nickname = s.Column("nickname", s.String, nullable=False)
    picture = s.Column("picture", s.String, nullable=False)
    email = s.Column("email", s.String, nullable=False)
    email_verified = s.Column("email_verified", s.String, nullable=False)
    updated_at = s.Column("updated_at", s.String, nullable=False)

    uploads = o.relationship("File", back_populates="uploader")
    audit_logs = o.relationship("AuditLog", back_populates="user")

    __table_args__ = (

    )


__all__ = ("User",)
