from __future__ import annotations

import sqlalchemy as s
import sqlalchemy.orm as o

from ..base import Base


class AuditLog(Base):
    """
    A record of an action done by an user.
    """
    __tablename__ = "auditlogs"

    id = s.Column(s.Integer, primary_key=True)

    user_id = s.Column(s.Integer, s.ForeignKey("users.id"), nullable=False)
    user = o.relationship("User", back_populates="audit_logs")

    action = s.Column(s.String, nullable=False)
    timestamp = s.Column(s.DateTime, nullable=False)

    obj = s.Column(s.Integer)

    __table_args__ = (

    )


__all__ = ("AuditLog",)
