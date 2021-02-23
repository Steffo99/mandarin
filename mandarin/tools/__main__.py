# Special imports
from __future__ import annotations

# External imports
import logging
import os
import pathlib
import time
import typing as t
import json

import click
import coloredlogs
import lyricsgenius
import requests
import toml
import numpy
import matplotlib.pyplot as plt

from .utils import MandarinAuth, LocalConfig
# Internal imports
from .utils import MandarinInstance, MANDARIN_INSTANCE_TYPE
from .utils import prints

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
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    nargs=-1,
)
@click.option(
    "-e", "--extension",
    help="If files are not specified, find all files with this extension in the current directory and upload them.",
    type=str,
    required=False,
)
@click.pass_context
def _(
        ctx: click.Context,
        files: t.Collection[str],
        extension: t.Optional[str],
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]
    auth: MandarinAuth = ctx.obj["AUTH"]

    def get_files(base_path) -> t.List[pathlib.Path]:
        f = []
        for obj in base_path.iterdir():
            obj: pathlib.Path
            if obj.is_dir():
                log.debug(f"Recursing into dir...")
                contents = get_files(obj)
                log.debug(f"Found {len(contents)} files.")
                f += contents
            elif obj.is_file():
                if obj.name.endswith(extension):
                    log.debug(f"Found new file: {obj}")
                    f.append(obj)
        return f

    if len(files) == 0 and extension:
        files = get_files(pathlib.Path("."))

    log.debug("Creating progress bar...")
    with click.progressbar(
            files,
            label="Uploading files",
            show_eta=True,
            show_percent=True,
            show_pos=True,
            item_show_func=lambda i: str(i)
    ) as bar:
        log.debug("Iterating over all files...")
        for path in bar:
            with open(path, mode="rb") as file:
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
@click.option(
    "--start-from",
    default=0,
    help="All song ids below this one will be skipped.",
    type=int,
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
        start_from: int,
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]
    auth: MandarinAuth = ctx.obj["AUTH"]
    genius = lyricsgenius.Genius(token, verbose=False)

    offset = 0
    last_time = time.time()
    while True:
        songs: t.List[t.Dict[str, t.Any]] = instance.get("/songs/", params={
            "limit": page_size,
            "offset": offset,
        }, headers=auth.data.token.access_header()).json()

        for song in songs:
            offset += 1

            if song["id"] < start_from:
                continue

            full_song: t.Dict[str, t.Any] = instance.get(
                f"/songs/{song['id']}",
                headers=auth.data.token.access_header()
            ).json()

            artist = " ".join([
                involvement["person"]["name"]
                for involvement in full_song["involvements"]
                if involvement["role"]["name"] == artist_role_name
            ])
            album = full_song["album"].get("title", "") if full_song.get("album") else ""

            click.secho(f"================================================================================")
            click.secho(f"{song['id']} | {full_song.get('title', '')} | {artist} | {album}")
            click.secho(f"--------------------------------------------------------------------------------")

            new_time = time.time()
            elapsed_time = new_time - last_time
            if elapsed_time <= delay:
                time.sleep(delay - elapsed_time)
            last_time = new_time

            try:
                data = genius.search_song(title=full_song["title"], artist=artist)
            except Exception as e:
                click.secho(f"{e}", bold=True, bg="red", fg="white")
                continue

            if data is None:
                click.secho("Not found", fg="red", dim=True)
                continue

            new_title = data.title if data.title else None
            new_description = data._body["description"]["plain"] if data._body.get("description") and data._body["description"]["plain"] != "?" else ""
            new_lyrics = data.lyrics if data.lyrics else None
            new_year = int(data._body["release_date"].split("-")[0]) if data._body.get("release_date") else None

            changes = False

            changes |= prints.old_to_new("Title", full_song["title"], new_title, active=scrape_title)
            if scrape_title:
                song["title"] = new_title

            changes |= prints.old_to_new("Description", full_song["description"], new_description, active=scrape_description)
            if scrape_description:
                song["description"] = new_description

            changes |= prints.old_to_new("Lyrics", full_song["lyrics"], new_lyrics, active=scrape_lyrics)
            if scrape_lyrics:
                song["lyrics"] = data.lyrics

            changes |= prints.old_to_new("Year", full_song["year"], new_year, active=scrape_year)
            if scrape_year:
                song["year"] = new_year

            if not changes:
                click.echo("Nothing to change, skipping...")
                continue

            if interactive:
                while True:
                    click.echo("Proceed? (y/n) ", nl=False)
                    choice = click.getchar(echo=True).lower()
                    click.echo()

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

        if len(songs) < page_size:
            break

        click.echo("All songs processed!")


@_group_auth.command("thesaurus")
@click.option(
    "-d", "--delay",
    help="The delay between two Mandarin requests.",
    default=1.0,
    type=float,
)
@click.argument(
    "file",
    type=click.File(mode="r", lazy=True),
    nargs=1
)
@click.pass_context
def _(
        ctx: click.Context,
        delay: float,
        file: t.TextIO,
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]
    auth: MandarinAuth = ctx.obj["AUTH"]

    j = json.load(file)

    def genre_dfs(supergenre: int, genre: str, children: dict, indent: int):
        prints.tree(indent, genre, has_children=len(children) > 0)

        r = instance.post(
            f"/genres/",
            json={
                "name": genre,
                "description": "",
                "supergenre_id": supergenre
            },
            headers=auth.data.token.access_header()
        )
        rj = r.json()

        if 200 <= r.status_code < 400:
            genre_id = rj["id"]
            prints.id_(genre_id, success=True)
        else:
            genre_id = rj["detail"]["id"]
            prints.id_(genre_id, success=False)
        click.echo()

        time.sleep(delay)

        for key, value in children.items():
            genre_dfs(supergenre=genre_id, genre=key, children=value, indent=indent + 1)

    for _key, _value in j.items():
        genre_dfs(supergenre=0, genre=_key, children=_value, indent=0)


@_group_auth.command("benchmark")
@click.option(
    "-d", "--delay",
    help="The delay between two Mandarin requests.",
    default=1.0,
    type=float,
)
@click.option(
    "-x", "--x-points",
    help="The number of points to create on the x axis.",
    default=25,
    type=int,
)
@click.argument(
    "file",
    type=click.File(mode="r", lazy=True),
    nargs=1
)
@click.pass_context
def _(
        ctx: click.Context,
        delay: float,
        x_points: int,
        file: t.TextIO,
):
    instance: MandarinInstance = ctx.obj["INSTANCE"]
    auth: MandarinAuth = ctx.obj["AUTH"]

    j = toml.load(file)

    queries = j.get("queries", [])
    if not queries:
        raise click.ClickException("No queries specified, nothing to do")

    parameters = j.get("parameters", [])
    if not parameters:
        raise click.ClickException("No parameters specified, nothing to do")

    weights = parameters.get("weight", [])
    if not weights:
        raise click.ClickException("No weights specified, nothing to do")

    normalizations = parameters.get("normalization", [])
    if not normalizations:
        raise click.ClickException("No normalizations specified, nothing to do")

    r_precisions = numpy.zeros((len(queries), len(weights), len(normalizations), x_points))
    r_interpolated = numpy.zeros((len(queries), len(weights), len(normalizations), x_points))

    for query_number, query in enumerate(queries):
        uin = query.get("uin", "")
        type_ = query["type"]
        text = query["text"]
        filter_ = query.get("filter")
        relevant = query["relevant"]

        fig, axs = plt.subplots(len(weights), len(normalizations), figsize=(48, 27), constrained_layout=True)
        fig.suptitle(uin, fontsize=20)

        click.secho(f"================================================================================")
        click.secho(uin, nl=False, bold=True)
        click.secho(f" | {type_!r} | {text!r} | {filter_!r}")
        click.secho(f"Relevant: {relevant!r}")
        click.secho(f"--------------------------------------------------------------------------------")

        for weight_number, weight in enumerate(weights):
            for normalization_number, normalization in enumerate(normalizations):

                try:
                    params = {
                        "element_type": type_,
                        "query": text,
                        "weight_a": weight.get("a", 0.0),
                        "weight_b": weight.get("b", 0.0),
                        "weight_c": weight.get("c", 0.0),
                        "weight_d": weight.get("d", 0.0),
                        "norm_1": bool(normalization.get("mode", 0) & 1),
                        "norm_2": bool(normalization.get("mode", 0) & 2),
                        "norm_4": bool(normalization.get("mode", 0) & 4),
                        "norm_8": bool(normalization.get("mode", 0) & 8),
                        "norm_16": bool(normalization.get("mode", 0) & 16),
                        "norm_32": bool(normalization.get("mode", 0) & 32),
                        **({"filter_genre_id": filter_} if filter_ else {})
                    }

                    results: t.List[t.Dict] = instance.get(
                        "/search/results" if filter_ is None else "/search/thesaurus",
                        params=params,
                        headers=auth.data.token.access_header()
                    ).json()

                    count = len(results)

                    if count >= 10:
                        click.secho("+ ", fg="green", nl=False)
                    elif count > 0:
                        click.secho(f"{count} ", fg="green", nl=False)
                    else:
                        click.secho("0 ", fg="yellow", nl=False)

                except Exception:
                    click.secho("X ", bg="red", fg="white", nl=False)
                    continue

                finally:
                    time.sleep(delay)

                # Create a graph
                relev_docs = 0
                total_docs = 0
                for result in results[:x_points]:
                    if result["id"] in relevant:
                        relev_docs += 1
                    total_docs += 1
                    r_precisions[query_number, weight_number, normalization_number, total_docs - 1] = \
                        relev_docs / total_docs

                for x in range(x_points):
                    r_interpolated[
                        query_number,
                        weight_number,
                        normalization_number,
                        x
                    ] = max(r_precisions[query_number, weight_number, normalization_number, x:])

                ax = axs[weight_number, normalization_number]
                ax.grid(b=True)
                ax.set_xticks(numpy.arange(0, x_points+5, 5))
                ax.set_xticks(numpy.arange(0, x_points+1, 1), minor=True)
                ax.set_yticks(numpy.arange(0, 1.25, 0.25))
                ax.set_yticks(numpy.arange(0, 1.05, 0.05), minor=True)
                ax.set_xlim([1, x_points])
                ax.set_ylim([0, 1.0])
                ax.plot(
                    [x+1 for x in range(x_points)],
                    r_precisions[query_number, weight_number, normalization_number, :],
                    label="Standard"
                )
                ax.plot(
                    [x+1 for x in range(x_points)],
                    r_interpolated[query_number, weight_number, normalization_number, :],
                    label="Interpolated"
                )
                ax.set_title(f"{weight['name']} + {normalization['name']}")
                ax.set_ylabel("Precision")

            click.secho()

        click.secho("Building plot...")
        fig.show()
        click.secho("Done!", fg="green")

    click.secho("Building average plot...")
    r_average = numpy.average(r_precisions, (0,))
    fig, axs = plt.subplots(len(weights), len(normalizations), figsize=(48, 27), constrained_layout=True)
    fig.suptitle("Average precision", fontsize=20)
    for weight_number in range(len(weights)):
        for normalization_number in range(len(normalizations)):
            ax = axs[weight_number, normalization_number]
            ax.grid(b=True)
            ax.set_xticks(numpy.arange(0, x_points+5, 5))
            ax.set_xticks(numpy.arange(0, x_points+1, 1), minor=True)
            ax.set_yticks(numpy.arange(0, 1.25, 0.25))
            ax.set_yticks(numpy.arange(0, 1.05, 0.05), minor=True)
            ax.set_xlim([1, x_points])
            ax.set_ylim([0, 1.0])
            ax.plot(
                [x+1 for x in range(x_points)],
                r_average[weight_number, normalization_number, :],
                label="Average"
            )
    fig.show()
    click.secho("Done!", fg="green")

    click.secho("Building mean average table...")
    fig, ax = plt.subplots(figsize=(13, 9))
    fig.suptitle("Mean average precision", fontsize=20)
    r_mean_average = numpy.average(r_average, (2,))
    ax.table(
        numpy.around(r_mean_average, 3),
        loc="center",
        rowLabels=list(map(lambda w: w["name"], weights)),
        colLabels=list(map(lambda n: n["name"], normalizations)),
    ),
    ax.axis("off")
    fig.show()
    click.secho("Done!", fg="green")


def main():
    _group_mandarin(auto_envvar_prefix="MANDARIN")


if __name__ == "__main__":
    main()
