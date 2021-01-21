# Special imports
from __future__ import annotations

# External imports
import logging

import click
import pydantic
import requests
import semver
import validators

# Special global objects
log = logging.getLogger(__name__)


# Code
class MandarinInstance(pydantic.BaseModel):
    url: str
    version: semver.VersionInfo

    class Config(pydantic.BaseConfig):
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.version} ({self.url!r})>"

    def __str__(self) -> str:
        return f"Mandarin {self.version} @ {self.url}"

    def absolute(self, path: str):
        return f"{self.url}{path}"

    def get(self, path: str, **kwargs):
        return requests.get(self.absolute(path), **kwargs)

    def post(self, path: str, **kwargs):
        return requests.post(self.absolute(path), **kwargs)

    def put(self, path: str, **kwargs):
        return requests.put(self.absolute(path), **kwargs)

    def delete(self, path: str, **kwargs):
        return requests.delete(self.absolute(path), **kwargs)

    def patch(self, path: str, **kwargs):
        return requests.patch(self.absolute(path), **kwargs)


class MandarinInstanceType(click.ParamType):
    name = "Mandarin instance"

    def convert(self, value, param, ctx):
        log.debug(f"Validating the instance URL: {value}")
        if not validators.url(value):
            log.info(f"Invalid URL: {value}")
            self.fail(f"Invalid URL: {value}")

        log.debug("Building Mandarin version URL...")
        version_url = f"{value}/version/package"

        log.debug(f"Getting Mandarin version at: {version_url!r}")
        try:
            r = requests.get(version_url)
        except requests.exceptions.ConnectionError as e:
            log.info(f"Could not connect to the Mandarin instance: {version_url!r}")
            self.fail(f"Could not connect to the Mandarin instance: {version_url!r}")

        log.debug(f"Response status: {r.status_code!r}")
        if r.status_code >= 400:
            log.info(f"Mandarin version check returned HTTP status: {r.status_code!r}")
            self.fail(f"Mandarin version check returned HTTP status: {r.status_code!r}")

        log.debug(f"Parsing response JSON...")
        version: str = r.json()

        log.debug(f"Parsing with semver: {version!r}")
        version: semver.VersionInfo = semver.VersionInfo.parse(version)
        log.debug(f"Version is: {version!r}")

        log.debug("Building MandarinInstance...")
        mi = MandarinInstance(url=value, version=version)
        log.info(f"Returning MandarinInstance: {mi!r}")
        return mi


MANDARIN_INSTANCE_TYPE = MandarinInstanceType()

# Objects exported by this module
__all__ = (
    "MandarinInstance",
    "MANDARIN_INSTANCE_TYPE",
)
