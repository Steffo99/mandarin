import expiringdict
import fastapi as f
import fastapi.openapi.models as fom
import fastapi.security.base as fsb
import fastapi.security.utils as fsu
import requests
import royalnet.lazy as l
import sqlalchemy.orm
from royalnet.typing import *

from mandarin.config import *
from mandarin.database.tables import *
from .db import *
from ..utils.loginsession import LoginSession


class LazyAuthorizationCodeBearer(fsb.SecurityBase):
    def __init__(self,
                 lazy_config: l.Lazy,
                 scheme_name: Optional[str] = None,
                 auto_error: Optional[bool] = True):
        super().__init__()
        self.lazy_config: l.Lazy = lazy_config
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: f.Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = fsu.get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise f.HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return param

    @property
    def model(self):
        return fom.OAuth2(flows=fom.OAuthFlows(
            authorizationCode={
                "authorizationUrl": self.lazy_config.evaluate()["auth.authorization"],
                "tokenUrl": self.lazy_config.evaluate()["auth.token"],
                "refreshUrl": self.lazy_config.evaluate()["auth.refresh"],
                "scopes": {
                    "profile": "[Required] Get location, nickname and picture",
                    "email": "[Required] Get email and email_verified",
                    "openid": "[Required] Additional OpenID Connect info"
                },
            }
        ))


# TODO: is max_len mandatory?
USER_INFO_CACHE = expiringdict.ExpiringDict(max_len=100, max_age_seconds=60 * 60 * 24)


def dependency_access_token(
        token: str = f.Security(LazyAuthorizationCodeBearer(lazy_config=lazy_config))
) -> JSON:
    if token not in USER_INFO_CACHE:
        user_info = requests.get(lazy_config.e["auth.userinfo"], headers={
            "Authorization": f"Bearer {token}"
        }).json()
        USER_INFO_CACHE[token] = user_info
    else:
        user_info = USER_INFO_CACHE[token]
    return user_info


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
    "LazyAuthorizationCodeBearer",
    "dependency_access_token",
    "LoginSession",
    "dependency_login_session",
)
