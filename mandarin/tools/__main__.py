# Special imports
from __future__ import annotations

# External imports
import logging
import os
import pathlib
import time
import typing as t

import click
import coloredlogs
import requests
import toml

# Internal imports
from .utils import MandarinInstance, MANDARIN_INSTANCE_TYPE

# Special global objects
log = logging.getLogger(__name__)


# Code
@click.group("mandarin")
@click.option(
    "-i", "--instance",
    help="The base url of the Mandarin instance to interact with.",
    required=True,
    type=MANDARIN_INSTANCE_TYPE,
)
@click.option(
    "-D", "--debug",
    help="Display the full debug log while running the command. Might break progress bars.",
    is_flag=True,
)
@click.pass_context
def _group_mandarin(
        ctx: click.Context,
        instance: MandarinInstance,
        debug: bool,
):
    coloredlogs.install(
        level="DEBUG" if debug else "WARNING",
        fmt="{asctime} {levelname} {name}: {message}",
        style="{",
        field_styles={
            "asctime": {"color": "white"},
            "levelname": {"color": "white", "bold": True},
            "name": {"color": "blue"},
        },
        level_styles={
            "debug": {"color": "white"},
            "info": {"color": "blue"},
            "warning": {"color": "yellow"},
            "error": {"color": "red"},
            "critical": {"color": "red", "bold": True},
        }
    )

    log.debug(f"Using: {instance!r}")
    click.echo(f"Using {instance}")
    ctx.ensure_object(dict)
    ctx.obj["INSTANCE"] = instance


@_group_mandarin.group("auth")
@click.option(
    "-f", "--file", "file_str",
    help="The file where authentication information should be stored in.",
    default=f"{pathlib.Path.home()}/.config/mandarin/auth.toml",
    type=click.Path(dir_okay=False, writable=True)
)
@click.option(
    "--client-id",
    help="The Client ID to use if requesting a new Device Code.",
    required=False,
    type=str,
)
@click.option(
    "--audience",
    help="The audience to use if requesting a new Device Code.",
    default="mandarin-api",
    type=str,
)
@click.pass_context
def _group_auth(
        ctx: click.Context,
        file_str: str,
        client_id: t.Optional[str],
        audience: str,
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]

    log.debug(f"Converting the string parameter to a path: {file_str!r}")
    file_path = pathlib.Path(file_str)
    dir_path = file_path.stem

    log.debug(f"Ensuring the path directories exist: {dir_path!r}")
    os.makedirs(dir_path, exist_ok=True)

    if not file_path.exists():
        log.debug(f"Creating auth file: {file_path!r}")
        with open(file_path, "w"):
            pass

    log.debug(f"Opening auth file: {file_path!r}")
    with open(file_path, "r+") as file:

        log.debug(f"Loading file as toml: {file!r}")
        global_data = toml.load(file)

        log.debug(f"Seeking back to the beginning...")
        file.seek(0)

        if instance.url not in global_data:

            # Phase 0: ensure options were specified

            if client_id is None:
                raise click.ClickException(
                    "--client-id was not specified and no tokens were ever generated for the instance."
                )

            # Phase 1: get auth config

            log.debug(f"Getting auth config for: {instance!r}")
            try:
                r = instance.get("/auth/config")
            except requests.exceptions.ConnectionError as e:
                raise click.ClickException(f"Could not retrieve Mandarin auth config due to a connection error: {e}")

            if r.status_code >= 400:
                raise click.ClickException(
                    f"Could not retrieve Mandarin auth config due to a HTTP error: {r.status_code}"
                )

            log.debug(f"Parsing Mandarin auth config...")
            try:
                instance_data: dict = r.json()
            except ValueError as e:
                log.info(f"Could not parse Mandarin auth config due to a JSON error: {e!r}")
                raise click.ClickException(f"Could not parse Mandarin auth config due to a JSON error: {e}")

            log.debug(f"Reading Mandarin auth config: {instance_data!r}")

            if device_code_url := instance_data.get("device"):
                log.debug(f"Device Codes can be obtained at: {device_code_url!r}")
            else:
                raise click.ClickException(f"Mandarin auth config is missing the 'device' key")

            if token_url := instance_data.get("token"):
                log.debug(f"Tokens can be exchanged at: {token_url!r}")
            else:
                raise click.ClickException(f"Mandarin auth config is missing the 'token' key")

            if user_info_url := instance_data.get("userinfo"):
                log.debug(f"User info can be obtained at: {user_info_url}")
            else:
                raise click.ClickException(f"Mandarin auth config is missing the 'userinfo' key")

            # Phase 2: get device code

            log.debug(f"Requesting a Device Code from: {device_code_url!r}")
            try:
                r = requests.post(device_code_url, data={
                    "client_id": client_id,
                    "audience": audience,
                    "scope": "profile email openid",  # Add more scopes here if required
                })
            except requests.exceptions.ConnectionError as e:
                raise click.ClickException(f"Could not request a Device Code due to a connection error: {e}")

            log.debug(f"Parsing Device Code response...")
            try:
                device_code_data: dict = r.json()
            except ValueError as e:
                raise click.ClickException(f"Could not parse Device Code response due to a JSON error: {e}")

            if r.status_code >= 400:
                raise click.ClickException(f"Device Code response contained HTTP status: {r.status_code!r}")

            if device_code := device_code_data.get("device_code"):
                log.debug(f"Found device code: {device_code!r}")
            else:
                raise click.ClickException(f"Device Code response is missing the 'device_code' key")

            if user_code := device_code_data.get("user_code"):
                log.debug(f"Found user code: {user_code!r}")
            else:
                raise click.ClickException(f"Device Code response is missing the 'user_code' key")

            if verification_uri_complete := device_code_data.get("verification_uri_complete"):
                log.debug(f"Found verification URL: {verification_uri_complete!r}")
            else:
                raise click.ClickException(f"Device Code response is missing the 'verification_uri_complete' key")

            if time_left := device_code_data.get("expires_in"):
                log.debug(f"Found seconds until expiration: {time_left!r}")
            else:
                raise click.ClickException(f"Device Code response is missing the 'expires_in' key")

            if interval := device_code_data.get("interval"):
                log.debug(f"Found interval: {interval!r}")
            else:
                raise click.ClickException(f"Device Code response is missing the 'interval' key")

            # Phase 3: wait for user authentication

            click.echo(f"To authorize Mandarin CLI, please login at: {verification_uri_complete}")
            click.echo(f"The following code should be displayed: {user_code}")

            while time_left:
                log.debug(f"Waiting for the interval to pass: {interval!r}s")
                time.sleep(interval)

                time_left -= interval
                log.debug(f"Time left: {time_left!r}s")

                log.debug(f"Requesting token at: {token_url!r}")
                r = requests.post(token_url, data={
                    "client_id": client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                })

                if r.status_code >= 400:
                    log.debug("Not authenticated yet, retrying...")
                    continue

                log.debug("Parsing token data...")
                token_data = r.json()
                break
            else:
                raise click.ClickException(f"Device verification URL expired. Please try logging in faster next time!")

            # Phase 4: validate token and get user info

            log.debug(f"Getting User Info...")
            try:
                r = requests.get(
                    user_info_url,
                    headers={
                        "Authorization": f"{token_data['token_type']} {token_data['access_token']}"
                    }
                )
            except requests.exceptions.ConnectionError as e:
                raise click.ClickException(f"Could not retrieve User Info due to a connection error: {e}")

            if r.status_code >= 400:
                raise click.ClickException(
                    f"Could not retrieve User Info due to a HTTP error: {r.status_code}"
                )

            log.debug(f"Parsing User Info...")
            try:
                user_info: dict = r.json()
            except ValueError as e:
                log.info(f"Could not parse User Info due to a JSON error: {e!r}")
                raise click.ClickException(f"Could not parse User Info due to a JSON error: {e}")

            if name := user_info.get("name"):
                log.debug(f"Found name: {name}")
            else:
                raise click.ClickException(f"User Info is missing the 'name' key")

            if sub := user_info.get("sub"):
                log.debug(f"Found sub: {name}")
            else:
                raise click.ClickException(f"User Info is missing the 'sub' key")

            log.debug("Integrating token data with instance_data...")
            instance_data["login_data"] = token_data

            log.debug("Writing instance data in global_data...")
            global_data[instance.url] = instance_data

            log.debug("Saving file as toml...")
            toml.dump(global_data, file)

            click.echo(f"Logged in as: {name!r} ({sub!r})")

    ctx.ensure_object(dict)
    ctx.obj["AUTH"] = global_data[instance.url]


@_group_auth.command("upload")
@click.argument(
    "files",
    type=click.File(mode="rb", lazy=True),
    nargs=-1,
)
@click.pass_context
def _(
        ctx: click.Context,
        files: t.Collection[t.BinaryIO]
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]
    auth: dict = ctx.obj["AUTH"]

    log.debug("Creating progress bar...")
    with click.progressbar(
            files,
            label="Uploading files",
            show_eta=True,
            show_percent=True,
            show_pos=True,
    ) as bar:
        log.debug("Iterating over all files...")
        for file in bar:
            file: t.BinaryIO
            log.debug(f"Uploading: {file.name!r}")

            try:
                r = instance.post(
                    "/files/layer",
                    params={
                        "generate_entries": True,
                    },
                    files={
                        "file": (file.name, file)
                    },
                    headers={
                        "Authorization": f"{auth['login_data']['token_type']} {auth['login_data']['access_token']}"
                    }
                )
            except requests.exceptions.ConnectionError as e:
                log.info(f"Could not connect to the upload endpoint: {e!r}")
                raise click.ClickException(f"Could not connect to the upload endpoint: {e}")

            log.debug(f"Response status: {r.status_code!r}")
            if r.status_code >= 400:
                log.info(f"File upload returned HTTP status: {r.status_code!r}")
                raise click.ClickException(f"File upload returned HTTP status: {r.status_code!r}")

            log.debug(f"Parsing response JSON...")
            j: str = r.json()
            log.debug(f"Parsed response: {j!r}")

    click.echo("Success!")


if __name__ == "__main__":
    _group_mandarin(auto_envvar_prefix="MANDARIN")
