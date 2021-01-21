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
import toml

# Internal imports
from .instance import MandarinInstance

# Special global objects
log = logging.getLogger(__name__)
Model = t.TypeVar("Model")


# Code
class LocalConfig(pydantic.BaseModel):
    client_id: str
    audience: str


class RemoteConfig(pydantic.BaseModel):
    authorization: str
    device: str
    token: str
    refresh: str
    userinfo: str
    openidcfg: str
    jwks: str


class UserInfo(pydantic.BaseModel):
    id: int
    sub: str
    name: str
    nickname: str
    picture: str
    email: str
    email_verified: str
    updated_at: datetime.datetime


class DeviceCodeResponse(pydantic.BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    expiration: datetime.datetime
    interval: int

    def is_valid(self) -> bool:
        return datetime.datetime.now() <= self.expiration


class TokenResponse(pydantic.BaseModel):
    access_token: str
    id_token: str
    token_type: str
    expires_in: int
    expiration: datetime.datetime

    def is_valid(self) -> bool:
        return datetime.datetime.now() <= self.expiration

    def access_header(self) -> t.Dict[str, str]:
        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

    def jwt_header(self) -> t.Dict[str, str]:
        return {
            "Authorization": f"{self.token_type} {self.id_token}"
        }


class InstanceData(pydantic.BaseModel):
    instance: MandarinInstance
    config: RemoteConfig
    token: TokenResponse


class JRequestError(Exception):
    pass


class JConnectionError(JRequestError):
    pass


class JStatusCodeError(JRequestError):
    pass


class JJSONDecodeError(JRequestError):
    pass


def jrequest(method: str, url: str, model: t.Type[Model], **kwargs) -> Model:
    r: requests.Response = requests.request(method=method, url=url, **kwargs)
    r.raise_for_status()
    j: dict = r.json()
    if "expires_in" in j:
        j["expiration"] = datetime.datetime.now() + datetime.timedelta(seconds=j["expires_in"])
    return model(**j)


@dataclasses.dataclass()
class MandarinAuth:
    instance: MandarinInstance
    local_config: LocalConfig
    remote_config: RemoteConfig
    token: TokenResponse
    user: UserInfo

    @classmethod
    def _load_storage_file(cls, file: t.TextIO) -> t.Dict[str, t.Any]:
        log.debug(f"Loading storage file: {file!r}")
        data = toml.load(file)

        log.debug(f"Seeking storage file back to the beginning...")
        file.seek(0)

        log.debug(f"Returning loaded data: {data!r}")
        return data

    @classmethod
    def _validate_token(cls, config: RemoteConfig, token: TokenResponse) -> t.Optional[UserInfo]:
        log.debug(f"Validating token: {token!r}")

        if not token.is_valid():
            log.debug(f"Token has expired: {token!r}")
            return None

        try:
            user_info = jrequest("GET", config.userinfo, UserInfo, headers=token.access_header())
        except requests.HTTPError as e:
            log.debug(f"UserInfo retrieval failed with an HTTP error: {e!r}")
            return None

        return user_info

    @classmethod
    def from_storage_file(
            cls,
            storage_file: t.TextIO,
            local_config: LocalConfig,
            instance: MandarinInstance,
    ) -> t.Optional[MandarinAuth]:
        global_data: t.Dict[str, dict] = cls._load_storage_file(file=storage_file)

        log.debug(f"Unpacking InstanceData for: {instance!r}")
        instance_data = global_data.get(instance.url)

        log.debug(f"Building InstanceData object from: {instance_data!r}")
        instance_data = InstanceData(**instance_data)

        log.debug(f"Loaded InstanceData: {instance_data!r}")

        user = cls._validate_token(config=instance_data.config, token=instance_data.token)

        if user is None:
            log.debug("Token validation failed, cannot create MandarinAuth")
            return None

        log.debug(f"Token validated, it belongs to: {user!r}")

        log.debug(f"Creating MandarinAuth...")
        return MandarinAuth(
            instance=instance,
            local_config=local_config,
            remote_config=instance_data.config,
            token=instance_data.token,
            user=user,
        )

    @classmethod
    def _fetch_remote_config(cls, instance: MandarinInstance) -> RemoteConfig:
        log.debug(f"Fetching RemoteConfig of: {instance!r}")

        return jrequest("GET", instance.absolute("/auth/config"), RemoteConfig)

    @classmethod
    def _get_device_code(cls, local_config: LocalConfig, remote_config: RemoteConfig) -> DeviceCodeResponse:
        log.debug(f"Fetching DeviceCodeResponse with {local_config=} and {remote_config=}")

        return jrequest("POST", remote_config.device, DeviceCodeResponse, data={
            "client_id": local_config.client_id,
            "audience": local_config.audience,
            "scope": "profile email openid",
        })

    @classmethod
    def _prompt_for_device_login(cls, url: str, user_code: str):
        log.debug("Prompting for device login")

        click.echo(click.style("=== AUTHORIZATION REQUIRED ===", bold=True))
        click.echo(f"Mandarin CLI needs to be logged in as an user to perform the requested action.")
        click.echo()
        click.echo(f"Please visit the following URL, check that the code matches with the one below and then "
                   f"complete the login: ")
        click.echo(click.style(url, fg="blue"))
        click.echo(click.style(user_code, fg="cyan", bold=True))

    @classmethod
    def _perform_device_login(
            cls,
            local_config: LocalConfig,
            remote_config: RemoteConfig,
            device_code: DeviceCodeResponse,
    ) -> TokenResponse:
        log.debug("Performing device login")

        cls._prompt_for_device_login(url=device_code.verification_uri_complete, user_code=device_code.user_code)

        seconds_left = device_code.expires_in
        interval = device_code.interval
        while seconds_left >= 0:
            log.debug(f"Waiting for {interval!r}s; {seconds_left!r}s until device code expiration.")
            time.sleep(interval)
            seconds_left -= interval

            try:
                return jrequest("POST", remote_config.token, TokenResponse, data={
                    "client_id": local_config.client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code.device_code
                })
            except requests.HTTPError:
                log.debug("User has not logged in yet, retrying...")
                continue

    @classmethod
    def from_login(
            cls,
            instance: MandarinInstance,
            local_config: LocalConfig,
    ) -> t.Optional[MandarinAuth]:
        remote_config = cls._fetch_remote_config(instance=instance)
        device_code = cls._get_device_code(local_config=local_config, remote_config=remote_config)
        token = cls._perform_device_login(
            local_config=local_config,
            remote_config=remote_config,
            device_code=device_code
        )

        user = cls._validate_token(config=remote_config, token=token)

        if user is None:
            log.debug("Token validation failed, cannot create MandarinAuth")
            return None

        log.debug(f"Token validated, it belongs to: {user!r}")

        log.debug(f"Creating MandarinAuth...")
        return MandarinAuth(
            instance=instance,
            local_config=local_config,
            remote_config=remote_config,
            token=token,
            user=user,
        )


# Objects exported by this module
__all__ = (
    "RemoteConfig",
    "UserInfo",
    "DeviceCodeResponse",
    "TokenResponse",
)
