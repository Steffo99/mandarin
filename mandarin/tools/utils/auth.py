# Special imports
from __future__ import annotations

import dataclasses
import datetime
# External imports
import logging
import time
import typing as t

import click
import pydantic
import requests

# Internal imports
from .instance import MandarinInstance

# Special global objects
log = logging.getLogger(__name__)
Model = t.TypeVar("Model")


# Code
def jrequest(method: str, url: str, model: t.Type[Model], **kwargs) -> Model:
    """
    .. todo:: Document :func:`.jrequest`.
    """
    r: requests.Response = requests.request(method=method, url=url, **kwargs)
    r.raise_for_status()
    j: dict = r.json()
    if "expires_in" in j:
        j["expiration"] = datetime.datetime.now() + datetime.timedelta(seconds=j["expires_in"])
    return model(**j)


class LocalConfig(pydantic.BaseModel):
    """
    OAuth2 Client configuration.
    """
    client_id: str
    audience: str


class RemoteConfig(pydantic.BaseModel):
    """
    Mandarin OAuth2 configuration.

    .. seealso:: :class:`mandarin.webapi.models.b_extras.AuthConfig`
    """
    authorization: str
    device: str
    token: str
    refresh: str
    userinfo: str
    openidcfg: str
    jwks: str

    @classmethod
    def from_instance(cls, instance: MandarinInstance) -> RemoteConfig:
        """
        Retrieve the :class:`.RemoteConfig` of a :class:`.MandarinInstance`.

        :param instance: The instance to retrieve the config of.
        :return: The retrieved config.
        """

        log.debug(f"Fetching RemoteConfig of: {instance!r}")
        return jrequest("GET", instance.absolute("/auth/config"), cls)


class DeviceCode(pydantic.BaseModel):
    """
    A device code and some other related information obtained from the ``/device/code`` OAuth2 server endpoint.
    """
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    expiration: datetime.datetime
    interval: int

    @classmethod
    def from_request(cls, local_config: LocalConfig, remote_config: RemoteConfig) -> DeviceCode:
        """
        Request a new device code from the OAuth2 server.

        :param local_config: The :class:`.LocalConfig` to use in the request.
        :param remote_config: The :class`.RemoteConfig` to use in the request.
        :return: The obtained :class:`.DeviceCode`.
        """
        log.debug(f"Fetching DeviceCodeResponse with {local_config=} and {remote_config=}")
        return jrequest("POST", remote_config.device, cls, data={
            "client_id": local_config.client_id,
            "audience": local_config.audience,
            "scope": "profile email openid",
        })

    def expired(self) -> bool:
        """
        :return: :data:`True` if the device code has expired, :data:`False` if it hasn't yet.
        """
        return datetime.datetime.now() >= self.expiration

    def login_prompt(self) -> None:
        """
        Display the login prompt for this device code in the terminal.
        """
        log.debug("Prompting for device login")

        click.echo(click.style("=== AUTHORIZATION REQUIRED ===", bold=True))
        click.echo(f"Mandarin CLI needs to be logged in as an user to perform the requested action.")
        click.echo()
        click.echo(f"Please visit the following URL, check that the code matches with the one below and then "
                   f"complete the login: ")
        click.echo(click.style(self.verification_uri_complete, fg="blue"))
        click.echo(click.style(self.user_code, fg="cyan", bold=True))


class BearerToken(pydantic.BaseModel):
    """
    A bearer token obtained by exchanging a code at the ``/token`` OAuth2 server endpoint.
    """
    access_token: str
    id_token: str
    token_type: str
    expires_in: int
    expiration: datetime.datetime

    @classmethod
    def from_device_code_exchange(
            cls,
            local_config: LocalConfig,
            remote_config: RemoteConfig,
            device_code: DeviceCode
    ) -> t.Optional[BearerToken]:
        """
        Obtain a bearer token by exchanging a :class:`.DeviceCode` with the OAuth2 server.

        :param local_config: The :class:`.LocalConfig` to use in the request.
        :param remote_config: The :class`.RemoteConfig` to use in the request.
        :param device_code: The :class:`.DeviceCode` to exchange.
        :return: The obtained :class:`.BearerToken`, or :data:`None` if the device code expired before the exchange was
                 possible.
        """
        while not device_code.expired():
            log.debug(f"Waiting for {device_code.interval!r}s")
            time.sleep(device_code.interval)
            try:
                return jrequest("POST", remote_config.token, BearerToken, data={
                    "client_id": local_config.client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code.device_code
                })
            except requests.HTTPError:
                log.debug("User has not logged in yet, retrying...")
                continue
        else:
            return None

    def expired(self) -> bool:
        """
        :return: :data:`True` if the token has expired, :data:`False` if it hasn't yet.
        """
        return datetime.datetime.now() >= self.expiration

    def access_header(self) -> t.Dict[str, str]:
        """
        Use the :attr:`access_token` as a HTTP ``Authorization`` header.

        :return: A dict with the header.
        """
        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

    def jwt_header(self) -> t.Dict[str, str]:
        """
        Use the :attr:`id_token` as a HTTP ``Authorization`` header.

        :return: A dict with the header.
        """
        return {
            "Authorization": f"{self.token_type} {self.id_token}"
        }


class AuthData(pydantic.BaseModel):
    """
    Authentication data for an instance which can be stored in a file.
    """

    instance: MandarinInstance
    config: RemoteConfig
    token: BearerToken

    def get_user_info(self) -> t.Optional[UserInfo]:
        """
        Using this :class:`AuthData`, validate the token and try retrieving its associated :class`.UserInfo`.

        :return: The :class:`.UserInfo` if the token is valid, or :data:`None` if it isn't.
        """
        log.debug(f"Getting UserInfo for: {self.token!r}")

        if self.token.expired():
            log.debug(f"Token has expired: {self.token!r}")
            return None

        try:
            user_info = jrequest("GET", self.config.userinfo, UserInfo, headers=self.token.access_header())
        except requests.HTTPError as e:
            log.debug(f"UserInfo retrieval failed with an HTTP error: {e!r}")
            return None

        return user_info

    @classmethod
    def from_storage_data(cls, data: t.Dict[str, t.Any], instance: MandarinInstance) -> t.Optional[AuthData]:
        """
        Retrieve the :class:`AuthData` of an instance from previously loaded storage data.

        :param data: The loaded storage data.
        :param instance: The instance to get the data of.
        :return: The :class:`AuthData` if it was stored, otherwise :data:`None`.

        .. seealso:: :meth:`.load_storage_file`
        """
        log.debug(f"Getting AuthConfig for: {instance!r}")
        auth_config = data.get(instance.url)

        if auth_config is None:
            return None

        log.debug(f"Building AuthConfig object from: {auth_config!r}")
        return cls(**auth_config)

    @classmethod
    def from_login(
            cls,
            instance: MandarinInstance,
            local_config: LocalConfig,
    ) -> t.Optional[AuthData]:
        """
        Create a new :class:`.AuthData` by requesting the user to perform the login procedure.

        :param instance: The instance to login on.
        :param local_config: The config of the local OAuth2 Client.
        :return: The created :class:`.AuthData` if the login is successful, :data:`None` otherwise.
        """
        remote_config = RemoteConfig.from_instance(instance=instance)
        device_code = DeviceCode.from_request(local_config=local_config, remote_config=remote_config)
        device_code.login_prompt()
        bearer_token = BearerToken.from_device_code_exchange(
            local_config=local_config,
            remote_config=remote_config,
            device_code=device_code
        )
        if bearer_token:
            return cls(
                instance=instance,
                config=remote_config,
                token=bearer_token,
            )
        else:
            return None


class UserInfo(pydantic.BaseModel):
    """
    Info about an user obtained from the `/userinfo` OAuth2 server endpoint.

    .. seealso:: :class:`mandarin.webapi.models.b_basic.User`
    """
    id: int
    sub: str
    name: str
    nickname: str
    picture: str
    email: str
    email_verified: str
    updated_at: datetime.datetime


@dataclasses.dataclass()
class MandarinAuth:
    """
    Authentication data for an instance completed with some runtime values.
    """
    data: AuthData
    user: UserInfo

    @classmethod
    def from_storage_file(
            cls,
            storage_data: t.Dict[str, t.Any],
            instance: MandarinInstance,
    ) -> t.Optional[MandarinAuth]:
        auth_data = AuthData.from_storage_data(data=storage_data, instance=instance)
        user_info = auth_data.get_user_info()
        if user_info is None:
            return None
        return cls(data=auth_data, user=user_info)

    @classmethod
    def from_device_login(
            cls,
            local_config: LocalConfig,
            instance: MandarinInstance,
    ) -> t.Optional[MandarinAuth]:
        auth_data = AuthData.from_login(instance=instance, local_config=local_config)
        user_info = auth_data.get_user_info()
        if user_info is None:
            return None
        return cls(data=auth_data, user=user_info)


# Objects exported by this module
__all__ = (
    "LocalConfig",
    "RemoteConfig",
    "DeviceCode",
    "BearerToken",
    "AuthData",
    "UserInfo",
    "MandarinAuth",
)
