from __future__ import annotations
from royalnet.typing import *
import fastapi as f

from ...database import *
from .. import models
from ..models import enums
from ..dependencies import *

router_auditlogs = f.APIRouter()


def ordered(query, column, order: enums.TimestampOrdering):
    if order is enums.TimestampOrdering.OLDEST_FIRST:
        query = query.order_by(column)
    elif order is enums.TimestampOrdering.LATEST_FIRST:
        query = query.order_by(column.desc())
    return query


@router_auditlogs.get(
    "/",
    summary="Get all audit logs.",
    responses={
        **login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
    order: enums.TimestampOrdering = f.Query(enums.TimestampOrdering.ANY,
                                             description="The order you want the objects to be returned in."),
):
    """
    Get an array of all audit logs currently in the database, in pages of `limit` elements and starting at the 
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ordered(ls.session.query(AuditLog), AuditLog.timestamp, order=order).limit(limit).offset(offset).all()


@router_auditlogs.get(
    "/by-user/{user_id}/",
    summary="Get the latest audit logs for an user.",
    responses={
        **login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get_by_user(
    ls: LoginSession = f.Depends(dependency_login_session),
    user_id: int = f.Path(..., description="The id of the user to get audit logs about."),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
    order: enums.TimestampOrdering = f.Query(enums.TimestampOrdering.ANY,
                                             description="The order you want the objects to be returned in."),
):
    """
    Get an array of the audit logs in which the specified user is involved, in pages of `limit` elements and
    starting at the element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    user = ls.get(User, user_id)
    return (
        ordered(ls.session.query(AuditLog).filter_by(user=user), AuditLog.timestamp, order=order)
        .limit(limit).offset(offset).all()
    )


@router_auditlogs.get(
    "/by-action/{action}/",
    summary="Get the latest audit logs about a certain action.",
    responses={
        **login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get_by_action(
    ls: LoginSession = f.Depends(dependency_login_session),
    action: str = f.Path(..., description="The action to get audit logs about. Uses SQL 'like' syntax. Case "
                                          "insensitive."),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
    order: enums.TimestampOrdering = f.Query(enums.TimestampOrdering.ANY,
                                             description="The order you want the objects to be returned in."),
):
    """
    Get an array of the audit logs that match the passed `action` pattern, in pages of `limit` elements and
    starting at the element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return (
        ordered(ls.session.query(AuditLog).filter(AuditLog.action.ilike(action)), AuditLog.timestamp, order=order)
        .limit(limit).offset(offset).all()
    )


__all__ = (
    "router_auditlogs",
)
