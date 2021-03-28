from __future__ import annotations
import royalnet.typing as t

import dataclasses
import datetime

import fastapi
import sqlalchemy.orm
from royalnet.typing import *

from ...database import tables

RowType = TypeVar("RowType")


@dataclasses.dataclass()
class LoginSession:
    user: tables.User
    session: sqlalchemy.orm.session.Session

    def get(self, table: Type[RowType], id_: Any) -> RowType:
        """
        Get the item with the specified id from a table, or raise a 404 error if the item doesn't exist.

        :param table: The table to get the item from.
        :param id_: The id to fetch.
        :return: The retrieved item.
        :raises fastapi.HTTPException: If the item was not found.
        """
        obj = self.session.query(table).get(id_)
        if obj is None:
            raise fastapi.HTTPException(404, f"The id '{id_}' does not match any {table.__name__}.")
        return obj

    def group(self, table: Type[RowType], ids: List[int]) -> Sequence[RowType]:
        """
        Get the items with the specified ids from the database.

        :param table: The table to get the items from.
        :param ids: The ids to fetch.
        :return: The retrieved items.
        """
        return self.session.query(table).filter(table.id.in_(ids)).all()

    def log(self, action: str, obj: t.Optional[int]) -> tables.AuditLog:
        """
        Log an action and add it to the session.

        :param action: The action to log.
        :param obj: The object to log information about.
        :return: The created AuditLog object.
        """
        session = sqlalchemy.orm.session.Session.object_session(self)
        audit_log = tables.AuditLog(user=self, action=action, timestamp=datetime.datetime.now(), obj=obj)
        session.add(audit_log)
        return audit_log


__all__ = (
    "LoginSession",
)
