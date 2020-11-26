from royalnet.typing import *
import os
import pathlib
import hashlib
import mimetypes
import sqlalchemy.orm
import copy
import mutagen
import logging
import shutil

from ..celery import app as celery
from ...config import config
from ...database import tables, Session

log = logging.getLogger(__name__)


def parse_tag(file: mutagen.File) -> mutagen.Tags:
    tag: mutagen.Tags = copy.deepcopy(file.tags)
    return tag


def strip_tag(file: mutagen.File) -> None:
    file.delete()


def save_with_no_padding(file: mutagen.File) -> None:
    file.save(padding=lambda _: 0)


def parse_and_strip_tags(path: os.PathLike) -> mutagen.Tags:
    file: mutagen.File = mutagen.File(filename=path)
    tag = parse_tag(file)
    strip_tag(file)
    save_with_no_padding(file)
    return tag


HASH_CHUNK_SIZE = 8192


def hash_file(path: os.PathLike) -> hashlib.sha512:
    h = hashlib.sha512()
    with open(path, "rb") as file:
        while chunk := file.read(HASH_CHUNK_SIZE):
            h.update(chunk)
    return h


def determine_extension(path: os.PathLike) -> str:
    _, ext = os.path.splitext(path)
    return ext


def determine_filename(path: os.PathLike) -> pathlib.Path:
    filename = hash_file(path).hexdigest()
    extension = determine_extension(path)
    musicdir = pathlib.Path(config["storage.music.dir"])
    return musicdir.joinpath(f"{filename}{extension}")


def copy_file(source: os.PathLike, destination: os.PathLike) -> None:
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copy2(source, destination)


def move_file(source: os.PathLike, destination: os.PathLike) -> None:
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    os.replace(source, destination)


def guess_mimetypes(path: os.PathLike) -> Tuple[Optional[str], Optional[str]]:
    return mimetypes.guess_type(path, strict=False)


def field_str(field: Optional[str]) -> Optional[str]:
    if field is None or field == "":
        return ""
    return field.strip()


def field_list(field: Optional[str]) -> List[str]:
    field = field_str(field)
    if field is None:
        return []
    return [item.strip() for item in field.split("/")]


def field_int(field: Optional[str]) -> Optional[int]:
    field = field_str(field)
    if field is None:
        return None
    try:
        return int(field)
    except ValueError:
        return None


def find_album_from_tag(session: sqlalchemy.orm.session.Session, tag: mutagen.Tags) -> Optional[tables.Album]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])

    query = None
    for artist in field_list(tag.get("albumartist")):
        subquery = (
            session.query(tables.AlbumInvolvement)
                   .filter(tables.AlbumInvolvement.role == role_artist)
                   .join(tables.Person)
                   .filter(tables.Person.name == field_str(tag.get("artist")))
                   .join(tables.Album)
                   .filter(tables.Album.title == field_str(tag.get("album")))
        )
        if query is None:
            query = subquery
        else:
            query = subquery.filter(tables.AlbumInvolvement.person_id.in_([person.id for person in query.all()]))

    album_involvement: Optional[tables.AlbumInvolvement] = query.one_or_none() if query else None
    if album_involvement:
        return album_involvement.album
    return None


def find_song_from_tag(session: sqlalchemy.orm.session.Session, tag: mutagen.Tags) -> Optional[tables.Song]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])

    query = None
    for artist in field_list(tag.get("albumartist")):
        subquery = (
            session.query(tables.SongInvolvement)
                   .filter(tables.SongInvolvement.role == role_artist)
                   .join(tables.Person)
                   .filter(tables.Person.name == artist)
                   .join(tables.Song)
                   .filter(tables.Song.title == field_str(tag.get("title")))
                   .join(tables.Album)
                   .filter(tables.Album.title == field_str(tag.get("album")))
        )
        if query is None:
            query = subquery
        else:
            query = subquery.filter(tables.SongInvolvement.person_id.in_([person.id for person in query.all()]))

    song_involvement: tables.SongInvolvement = query.one_or_none() if query else None
    if song_involvement:
        return song_involvement.song
    return None


def make_entries_from_layer(session: sqlalchemy.orm.session.Session,
                            layer: tables.Layer,
                            tag: mutagen.Tags) -> Tuple[tables.Album, tables.Song]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])
    role_composer = tables.Role.make(session=session, name=config["apps.files.roles.composer"])
    role_performer = tables.Role.make(session=session, name=config["apps.files.roles.performer"])

    album = find_album_from_tag(session=session, tag=tag)
    if album is None:
        album = tables.Album(
            title=field_str(tag.get("album"))
        )
        album.involve(
            people=(tables.Person.make(session=session, name=name) for name in field_list(tag.get("artist"))),
            role=role_artist
        )

    song = find_song_from_tag(session=session, tag=tag)
    if song is None:
        song_genre = field_str(tag.get("genre"))
        song = tables.Song(
            title=field_str(tag.get("title")),
            year=field_int(tag.get("date")),
            disc=field_int(tag.get("discnumber")),
            track=field_int(tag.get("tracknumber")),
            album=album,
            genres=[tables.Genre.make(session=session, name=song_genre)] if song_genre else [],
        )
        song.involve(
            people=(tables.Person.make(session=session, name=name) for name in field_list(tag.get("artist"))),
            role=role_artist
        )
        song.involve(
            people=(tables.Person.make(session=session, name=name) for name in field_list(tag.get("composer"))),
            role=role_composer
        )
        song.involve(
            people=(tables.Person.make(session=session, name=name) for name in field_list(tag.get("performer"))),
            role=role_performer
        )

    layer.song = song

    return album, song


@celery.task
def process_music(path: os.PathLike,
                  uploader_id: Optional[int] = None,
                  *,
                  layer_data: Optional[Dict[str, Any]] = None,
                  generate_entries: bool = False,
                  delete_original: bool = False):

    if layer_data is None:
        layer_data: Dict[str, Any] = {}

    session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    tag: mutagen.Tags = parse_and_strip_tags(path)

    destination = determine_filename(path)
    mime_type, mime_software = guess_mimetypes(path)

    file: Optional[tables.File] = None
    if os.path.exists(destination):
        file = session.query(tables.File).filter_by(name=destination.name).one_or_none()
    else:
        if delete_original:
            move_file(source=path, destination=destination)
        else:
            copy_file(source=path, destination=destination)
    if file is None:
        file = tables.File(
            name=destination.name,
            mime_type=mime_type,
            mime_software=mime_software,
            uploader_id=uploader_id
        )
        session.add(file)

    layer = tables.Layer(
        **layer_data,
        file=file,
    )
    session.add(layer)

    if generate_entries:
        album, song = make_entries_from_layer(session=session, layer=layer, tag=tag)
        session.add(album)
        session.add(song)

    session.commit()


__all__ = (
    "process_music",
)
