# Special imports
from __future__ import annotations

# External imports
import logging
import typing as t

import click
import requests

# Internal imports
from .utils import MandarinInstance, MANDARIN_INSTANCE_TYPE

# Special global objects
log = logging.getLogger(__name__)


# Code
@click.group()
@click.option(
    "-i", "--instance",
    help="The base url of the Mandarin instance to interact with.",
    required=True,
    type=MANDARIN_INSTANCE_TYPE,
)
@click.pass_context
def instanceful(
        ctx: click.Context,
        instance: MandarinInstance,
):
    log.debug(f"Using: {instance!r}")
    click.echo(f"Using {instance}")
    ctx.ensure_object(dict)
    ctx.obj["INSTANCE"] = instance


@instanceful.command()
@click.argument(
    "files",
    type=click.File(mode="rb", lazy=True),
    nargs=-1,
)
@click.pass_context
def upload(
        ctx: click.Context,
        files: t.Collection[t.BinaryIO]
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]

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


if __name__ == "__main__":
    instanceful()
