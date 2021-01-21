from __future__ import annotations

import dataclasses

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
        obj = self.session.query(table).get(id_)
        if obj is None:
            raise fastapi.HTTPException(404, f"The id '{id_}' does not match any {table.__name__}.")
        return obj

    def group(self, table: Type[RowType], ids: List[int]) -> Sequence[RowType]:
        return self.session.query(table).filter(table.id.in_(ids)).all()


__all__ = (
    "LoginSession",
)
