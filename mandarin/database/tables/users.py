import datetime

import royalnet.alchemist as a
import sqlalchemy as s
import sqlalchemy.orm as o
from royalnet.typing import *

from .auditlogs import AuditLog
from ..base import Base


class User(Base, a.ColRepr, a.Updatable):
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

    def log(self, action: str, obj: Optional[int]) -> AuditLog:
        """
        Log an action and add it to the session.
        """
        session = o.session.Session.object_session(self)
        audit_log = AuditLog(user=self, action=action, timestamp=datetime.datetime.now(), obj=obj)
        session.add(audit_log)
        return audit_log


__all__ = ("User",)
