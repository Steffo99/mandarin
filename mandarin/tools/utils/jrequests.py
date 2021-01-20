# Module docstring
"""
Some utilities to perform a Device Code OAuth login.
"""

# Special imports
from __future__ import annotations

# External imports
import logging
import typing as t

import click
import requests

# Internal imports
# from . import something

# Special global objects
log = logging.getLogger(__name__)


# Code
def key(obj: dict, name: str, operation: str) -> t.Any:
    value = obj.get(name)
    if value:
        log.debug(f"Parsed {operation} key {name!r}: {value!r}")
        return value
    else:
        raise click.ClickException(f"{operation} is missing the {name!r} key")


def keep(obj: dict, keys: t.List[str], operation: str) -> dict:
    result = {}
    for k in keys:
        result[k] = key(obj, k, operation)
    return result


class RequestError(click.ClickException):
    pass


class HTTPError(click.ClickException):
    pass


class JSONError(click.ClickException):
    pass


def request(method: t.Callable, *args, keys: t.List[str], operation: str, **kwargs):
    try:
        r: requests.Response = method(*args, **kwargs)
    except requests.exceptions.ConnectionError as e:
        raise RequestError(f"Could not retrieve {operation} due to a connection error: {e}")

    if r.status_code >= 400:
        raise HTTPError(f"Could not retrieve {operation} due to a HTTP error: {r.status_code}")

    log.debug(f"Parsing {operation} JSON: {r.text!r}")
    try:
        j: dict = r.json()
    except ValueError as e:
        raise JSONError(f"Could not parse Mandarin auth config due to a JSON error: {e}")

    log.debug(f"Parsed {operation} as dict: {j!r}")
    return keep(j, keys, operation)


# Objects exported by this module
__all__ = (
    "",
)
