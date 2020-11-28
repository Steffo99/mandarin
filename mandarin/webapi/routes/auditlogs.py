from __future__ import annotations
from royalnet.typing import *
import fastapi as f

from ...database import tables
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses

router_auditlogs = f.APIRouter()


def ordered(query, column, order: models.enums.TimestampOrdering):
    if order is models.enums.TimestampOrdering.OLDEST_FIRST:
        query = query.order_by(column)
    elif order is models.enums.TimestampOrdering.LATEST_FIRST:
        query = query.order_by(column.desc())
    return query


@router_auditlogs.get(
    "/",
    summary="Get all audit logs.",
    responses={
        **responses.login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
    order: models.enums.TimestampOrdering = f.Query(models.enums.TimestampOrdering.ANY,
                                                    description="The order you want the objects to be returned in."),
):
    """
    Get an array of all audit logs currently in the database, in pages of `limit` elements and starting at the 
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ordered(ls.session.query(tables.AuditLog), tables.AuditLog.timestamp, order=order).limit(limit).offset(offset).all()


@router_auditlogs.get(
    "/by-user/{user_id}/",
    summary="Get the latest audit logs for an user.",
    responses={
        **responses.login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get_by_user(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    user_id: int = f.Path(..., description="The id of the user to get audit logs about."),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
    order: models.enums.TimestampOrdering = f.Query(models.enums.TimestampOrdering.ANY,
                                                    description="The order you want the objects to be returned in."),
):
    """
    Get an array of the audit logs in which the specified user is involved, in pages of `limit` elements and
    starting at the element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    user = ls.get(tables.User, user_id)
    return (
        ordered(ls.session.query(tables.AuditLog).filter_by(user=user), tables.AuditLog.timestamp, order=order)
        .limit(limit).offset(offset).all()
    )


@router_auditlogs.get(
    "/by-action/{action}/",
    summary="Get the latest audit logs about a certain action.",
    responses={
        **responses.login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get_by_action(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    action: str = f.Path(..., description="The action to get audit logs about. Uses SQL 'like' syntax. Case "
                                          "insensitive."),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
    order: models.enums.TimestampOrdering = f.Query(models.enums.TimestampOrdering.ANY,
                                                    description="The order you want the objects to be returned in."),
):
    """
    Get an array of the audit logs that match the passed `action` pattern, in pages of `limit` elements and
    starting at the element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return (
        ordered(ls.session.query(tables.AuditLog).filter(tables.AuditLog.action.ilike(action)), tables.AuditLog.timestamp, order=order)
        .limit(limit).offset(offset).all()
    )


__all__ = (
    "router_auditlogs",
)
