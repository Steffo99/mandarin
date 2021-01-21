"""
Extra models are :class:`.MandarinModel`\\ s which represent data not contained in the database.
"""

from . import a_base as base


class AuthConfig(base.MandarinModel):
    authorization: str
    device: str
    token: str
    refresh: str
    userinfo: str
    openidcfg: str
    jwks: str


__all__ = (
    "AuthConfig",
)
