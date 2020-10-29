from royalnet.typing import *
import fastapi as f
import fastapi.security as fs
import jose.jwt
import requests
import starlette.status as s

from ..config import *
from ..database.tables import *
from .database import *


auth0_scheme = fs.OAuth2AuthorizationCodeBearer(
    authorizationUrl=config["auth.authorization"],
    tokenUrl=config["auth.token"],
    scopes={
        "profile": "[Required] Get name, nickname and picture",
        "email": "[Required] Get email and email_verified",
        "openid": "[Required] Additional OpenID Connect info"
    }
)


def validate_access_token(token: str = f.Depends(auth0_scheme)):
    # May want to cache this
    return requests.get(config["auth.userinfo"], headers={
        "Authorization": f"Bearer {token}"
    }).json()


def find_or_create_user(payload: JSON = f.Depends(validate_access_token)) -> User:
    session = Session()
    user = session.query(User).filter_by(sub=payload["sub"]).one_or_none()
    if user is None:
        user = User(**payload)
        session.add(user)
    else:
        for key, value in payload.items():
            user.__setattr__(key, value)
    session.commit()
    session.close()
    return user
