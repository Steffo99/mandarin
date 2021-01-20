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
from .utils import jrequests as jr

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

            auth_config = jr.request(instance.get, "/auth/config", operation="Auth Config", keys=[
                "authorization",
                "device",
                "token",
                "refresh",
                "userinfo",
                "openidcfg",
                "jwks",
            ])

            # Phase 2: get device code

            device_request = jr.request(
                requests.post,
                auth_config["device"],
                operation="Device Request",
                keys=[
                    "device_code",
                    "user_code",
                    "verification_uri",
                    "expires_in",
                    "interval",
                ],
                data={
                    "client_id": client_id,
                    "audience": audience,
                    "scope": "profile email openid",
                }
            )

            # Phase 3: wait for user authentication

            click.echo(f"To authorize Mandarin CLI, you will need to login at the following URL:")
            click.echo(click.style(device_request["verification_uri"], fg="blue", bold=True))
            click.echo()
            click.echo(f"Once there, you will have to input the following code:")
            click.echo(click.style(device_request["user_code"], fg="yellow", bold=True))

            seconds_left = device_request["expires_in"]
            interval = device_request["interval"]

            while seconds_left >= 0:
                log.debug(f"Waiting for {interval!r}s, {seconds_left!r}s until expiration.")
                time.sleep(interval)
                seconds_left -= interval

                try:
                    token_request = jr.request(
                        requests.post,
                        auth_config["token"],
                        operation="Token Request",
                        keys=[
                            "access_token",
                            "id_token",
                            "token_type",
                            "expires_in",
                        ],
                        data={
                            "client_id": client_id,
                            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                            "device_code": device_request["device_code"]
                        }
                    )
                except jr.HTTPError:
                    log.debug("Not authenticated yet, retrying...")
                else:
                    break

            else:
                raise click.ClickException(f"Device verification URL expired. Please try logging in faster next time!")

            # Phase 4: validate token and get user info

            user_info = jr.request(
                requests.get,
                auth_config["userinfo"],
                operation="User Info",
                keys=[
                    "sub",
                    "name",
                    "nickname",
                    "email",
                    "email_verified",
                    "updated_at",
                ],
                headers={
                    "Authorization": f"{token_request['token_type']} {token_request['access_token']}"
                }
            )

            # Phase 5: store all data

            instance_data = {
                "config": auth_config,
                "token": token_request,
                "user": user_info,
            }

            log.debug("Writing instance data in global_data...")
            global_data[instance.url] = instance_data

            log.debug("Saving file as toml...")
            toml.dump(global_data, file)

            click.echo(f"Logged in as: {user_info['name']} ({user_info['sub']})")

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
