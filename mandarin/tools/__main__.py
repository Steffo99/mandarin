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
import lyricsgenius
import requests
import toml

from .utils import MandarinAuth, LocalConfig
# Internal imports
from .utils import MandarinInstance, MANDARIN_INSTANCE_TYPE
from .utils import old_to_new

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

        storage_data[instance.url] = auth.data.dict()
        toml.dump(storage_data, file)

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
    auth: MandarinAuth = ctx.obj["AUTH"]

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
                    headers=auth.data.token.access_header(),
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


@_group_auth.command("genius")
@click.option(
    "-g", "--genius-token", "token",
    required=True,
    help="The Genius access token to use for data retrieval.",
    type=str,
)
@click.option(
    "--scrape-title/--keep-title",
    default=True,
    help="Whether the original song title should be kept or scraped from Genius.",
    type=bool,
)
@click.option(
    "--scrape-description/--keep-description",
    default=True,
    help="Whether the original song description should be kept or scraped from Genius.",
    type=bool,
)
@click.option(
    "--scrape-lyrics/--keep-lyrics",
    default=False,
    help="Whether the original song lyrics should be kept or scraped from Genius.",
    type=bool,
)
@click.option(
    "--scrape-year/--keep-year",
    default=True,
    help="Whether the original song year should be kept or scraped from Genius.",
    type=bool,
)
@click.option(
    "-d", "--delay",
    default=1.0,
    help="The delay to use between Genius info fetches. Don't get rate limited!",
    type=float,
)
@click.option(
    "--artist-role-name",
    default="Artist",
    help="The name of the role artists have on your Mandarin instance.",
    type=str,
)
@click.option(
    "--page-size",
    default=500,
    help="The maximum page size for requests on your Mandarin instance.",
    type=int,
)
@click.option(
    "--interactive/--automatic",
    default=True,
    help="Whether this tool should prompt for confirmation on every song processed.",
    type=bool,
)
@click.pass_context
def _(
        ctx: click.Context,
        token: str,
        scrape_title: bool,
        scrape_description: bool,
        scrape_lyrics: bool,
        scrape_year: bool,
        delay: float,
        artist_role_name: str,
        page_size: int,
        interactive: bool,
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]
    auth: MandarinAuth = ctx.obj["AUTH"]
    genius = lyricsgenius.Genius(token, verbose=False)

    count = instance.get("/songs/count").json()

    offset = 0
    while True:
        songs: t.List[t.Dict[str, t.Any]] = instance.get("/songs/", params={
            "limit": page_size,
            "offset": offset,
        }, headers=auth.data.token.access_header()).json()

        for song in songs:
            try:
                offset += 1
                click.echo(f"Song {offset} / {count}")

                full_song: t.Dict[str, t.Any] = instance.get(
                    f"/songs/{song['id']}",
                    headers=auth.data.token.access_header()
                ).json()

                # Search for the song on Genius
                artist = " ".join([
                    involvement["person"]["name"]
                    for involvement in full_song["involvements"]
                    if involvement["role"] == artist_role_name
                ])
                data = genius.search_song(title=full_song["title"], artist=artist)

                new_title = data.title if data.title else None
                new_description = data._body["description"]["plain"] if "description" in data._body else None
                new_lyrics = data.lyrics if data.lyrics else None
                new_year = int(data.release_date.split("-")[0]) if data.release_date else None

                changes = False

                if scrape_title:
                    changes |= old_to_new(full_song["title"], new_title)
                    song["title"] = new_title

                if scrape_description:
                    changes |= old_to_new(full_song["description"], new_description)
                    song["description"] = new_description

                if scrape_lyrics:
                    changes |= old_to_new(full_song["lyrics"], new_lyrics)
                    song["lyrics"] = data.lyrics

                if scrape_year:
                    changes |= old_to_new(full_song["year"], new_year)
                    song["year"] = new_year

                if not changes:
                    click.echo("Nothing to change, skipping...")
                    continue

                if interactive:
                    while True:
                        click.echo("Proceed? (y/n) ", nl=False)
                        choice = click.getchar(echo=True).lower()

                        if choice == "y":
                            instance.put(
                                f"/songs/{song['id']}",
                                json=song,
                                headers=auth.data.token.access_header()
                            )
                            break
                        elif choice == "n":
                            break
                else:
                    instance.put(
                        f"/songs/{song['id']}",
                        json=song,
                        headers=auth.data.token.access_header()
                    )

            finally:
                time.sleep(delay)

        if len(songs) <= page_size:
            break

        click.echo("All songs processed!")


if __name__ == "__main__":
    _group_mandarin(auto_envvar_prefix="MANDARIN")
