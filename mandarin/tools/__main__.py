# Special imports
from __future__ import annotations

# External imports
import logging
import os
import pathlib
import typing as t

import click
import coloredlogs
import requests
import toml

from .utils import MandarinAuth, LocalConfig
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
    default=f"{pathlib.Path.home()}/.config/mandarin/cli/auth.toml",
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
    required=False,
    type=str,
)
@click.pass_context
def _group_auth(
        ctx: click.Context,
        file_str: str,
        client_id: t.Optional[str],
        audience: t.Optional[str],
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]

    log.debug(f"Converting the string parameter to a path: {file_str!r}")
    file_path = pathlib.Path(file_str)
    dir_path = file_path.parent

    log.debug(f"Ensuring the path directories exist: {dir_path!r}")
    os.makedirs(dir_path, exist_ok=True)

    if not file_path.exists():
        log.debug(f"Creating storage file: {file_path!r}")
        with open(file_path, "w"):
            pass

    log.debug(f"Opening storage file: {file_path!r}")
    with open(file_path, "r+") as file:

        log.debug(f"Loading storage file: {file!r}")
        storage_data = toml.load(file)

        log.debug(f"Seeking storage file back to the beginning...")
        file.seek(0)

        auth = None
        if storage_data:
            auth = MandarinAuth.from_storage_file(
                storage_data=storage_data,
                instance=instance,
            )

        if not auth:
            if not (client_id and audience):
                raise click.ClickException("To authenticate, a --client-id and an --audience are required.")

            auth = MandarinAuth.from_device_login(
                local_config=LocalConfig(client_id=client_id, audience=audience),
                instance=instance
            )

        if not auth:
            raise click.ClickException("Failed to authenticate.")

        storage_data[instance.url] = auth
        toml.dump(file)

    ctx.ensure_object(dict)
    ctx.obj["AUTH"] = auth


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
                        "Authorization": f"{auth['token']['token_type']} {auth['token']['access_token']}"
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
