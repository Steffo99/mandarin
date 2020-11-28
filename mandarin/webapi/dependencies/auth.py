from royalnet.typing import *
import fastapi as f
import fastapi.security as fs
import requests
import sqlalchemy.orm
import dataclasses
from mandarin.config import *
from mandarin.database.tables import *
from mandarin.database.engine import *

from .db import *
from ..utils.loginsession import LoginSession


auth0_scheme = fs.OAuth2AuthorizationCodeBearer(
    authorizationUrl=config["auth.authorization"],
    tokenUrl=config["auth.token"],
    scopes={
        "profile": "[Required] Get name, nickname and picture",
        "email": "[Required] Get email and email_verified",
        "openid": "[Required] Additional OpenID Connect info"
    }
)


def dependency_access_token(
    token: str = f.Depends(auth0_scheme)
) -> JSON:
    # May want to cache this
    return requests.get(config["auth.userinfo"], headers={
        "Authorization": f"Bearer {token}"
    }).json()


def dependency_login_session(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    payload: JSON = f.Depends(dependency_access_token)
) -> LoginSession:
    user = session.query(User).filter_by(sub=payload["sub"]).one_or_none()
    if user is None:
        user = User(**payload)
        session.add(user)
    else:
        for key, value in payload.items():
            user.__setattr__(key, value)
    session.commit()
    return LoginSession(user=user, session=session)


__all__ = (
    "auth0_scheme",
    "dependency_access_token",
    "LoginSession",
    "dependency_login_session",
)
