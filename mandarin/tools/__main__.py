# Special imports
from __future__ import annotations

# External imports
import logging
import os
import pathlib
import time
import typing as t

import click
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
@click.pass_context
def _group_mandarin(
        ctx: click.Context,
        instance: MandarinInstance,
):
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

            # Phase 1: get static data

            log.debug(f"Getting auth config data for: {instance!r}")
            try:
                r = instance.get("/auth/config")
            except requests.exceptions.ConnectionError as e:
                log.info(f"Could not retrieve auth config of the Mandarin instance")
                raise click.ClickException(f"Could not retrieve auth config of the Mandarin instance")

            log.debug(f"Response status: {r.status_code!r}")
            if r.status_code >= 400:
                log.info(f"Mandarin auth config retrieval returned HTTP status: {r.status_code!r}")
                raise click.ClickException(f"Mandarin auth config retrieval returned HTTP status: {r.status_code!r}")

            log.debug(f"Parsing response JSON...")
            instance_data: dict = r.json()

            # Phase 2: get token

            device_code_url = instance_data["device"]
            log.debug(f"Device Code URL is: {device_code_url!r}")

            token_url = instance_data["token"]
            log.debug(f"Token URL is: {token_url!r}")

            if client_id is None:
                raise click.ClickException("Client ID not specified.")

            log.debug(f"Requesting device code from: {device_code_url!r}")
            try:
                r = requests.post(device_code_url, data={
                    "client_id": client_id,
                    "audience": audience,
                    "scope": "profile email openid",  # Add more scopes here as required
                })
            except requests.exceptions.ConnectionError as e:
                log.info(f"Could not request device code from: {device_code_url!r}")
                raise click.ClickException(f"Could not request device code from: {device_code_url!r}")

            log.debug(f"Parsing response JSON...")
            device_code_data: dict = r.json()

            log.debug(f"Response status: {r.status_code!r}")
            if r.status_code >= 400:
                log.info(f"Device Code request returned HTTP status: {r.status_code!r}")
                raise click.ClickException(f"Device Code request returned HTTP status: {r.status_code!r}")

            device_code = device_code_data["device_code"]
            log.debug(f"Found device code: {device_code!r}")

            user_code = device_code_data["user_code"]
            log.debug(f"Found user code: {user_code!r}")

            verification_uri_complete = device_code_data["verification_uri_complete"]
            log.debug(f"Found verification URL: {verification_uri_complete!r}")

            time_left = device_code_data["expires_in"]
            log.debug(f"Found seconds until expiration: {time_left!r}")

            interval = device_code_data["interval"]
            log.debug(f"Found interval: {interval!r}")

            click.echo(f"To authorize Mandarin CLI, please login at: {verification_uri_complete}")
            click.echo(f"The following code should be displayed: {user_code}")

            while time_left:
                time.sleep(interval)

                time_left -= interval
                log.debug(f"Time left: {time_left}s")

                log.debug(f"Requesting token at: {token_url}")
                r = requests.post(token_url, data={
                    "client_id": client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                })

                if 400 <= r.status_code < 500:
                    log.debug("Not authenticated yet")
                    continue
                r.raise_for_status()

                log.debug("Parsing token data...")
                token_data = r.json()
                break
            else:
                raise click.ClickException(f"Device verification URL expired, please hurry up next time!")

            # TODO: Validate token and get user data

            log.debug("Integrating token data with instance_data...")
            instance_data["login_data"] = token_data

            log.debug("Writing instance data in global_data...")
            global_data[instance.url] = instance_data

            log.debug("Saving file as toml...")
            toml.dump(global_data, file)

            click.echo("Logged in successfully!")

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

    click.echo("Success!")


if __name__ == "__main__":
    _group_mandarin(auto_envvar_prefix="MANDARIN")
