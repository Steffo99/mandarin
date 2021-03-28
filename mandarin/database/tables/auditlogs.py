from __future__ import annotations

import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class AuditLog(Base):
    """
    A record of an action done by an user.
    """
    __tablename__ = "auditlogs"

    id = s.Column("id", s.Integer, primary_key=True)

    user_id = s.Column("user_id", s.Integer, s.ForeignKey("users.id"), nullable=False)
    user = o.relationship("User", back_populates="audit_logs")

    action = s.Column("action", s.String, nullable=False)
    timestamp = s.Column(s.DateTime, nullable=False)

    obj = s.Column("obj", s.Integer)


__all__ = ("AuditLog",)
