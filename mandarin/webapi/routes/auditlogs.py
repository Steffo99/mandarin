from __future__ import annotations
from royalnet.typing import *
import fastapi as f

from ...database import *
from .. import models
from ..dependencies import *

router_auditlogs = f.APIRouter()


@router_auditlogs.get(
    "/",
    summary="Get the latest audit logs.",
    responses={
        **login_error,
    },
    response_model=List[models.AuditLogOutput]
)
def get(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    return ls.session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset).all()


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
):
    user = ls.get(User, user_id)
    return (
        ls.session
            .query(AuditLog)
            .filter_by(user=user)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
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
):
    return (
        ls.session
            .query(AuditLog)
            .filter(AuditLog.action.ilike(action))
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
    )


__all__ = (
    "router_auditlogs",
)
