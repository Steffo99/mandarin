from __future__ import annotations
from royalnet.typing import *
from typing import IO
import os
import pathlib
import hashlib
import mimetypes
import sqlalchemy.orm
import mutagen
import logging
import io

from ..celery import app as celery
from ..utils import MutagenParse
from ...config import config
from ...database import tables, Session


log = logging.getLogger(__name__)


def parse_tag(file: mutagen.File) -> Dict[str, List[str]]:
    tag: Dict[str, List[str]] = dict(file.tags)
    return tag


def strip_tag(file: mutagen.File) -> None:
    file.tags.clear()


def save_with_no_padding(file: mutagen.File, destination_stream: IO[bytes]) -> None:
    file.save(fileobj=destination_stream, padding=lambda _: 0)


def process_tags(stream: IO[bytes]) -> MutagenParse:
    stream.seek(0)
    file: mutagen.File = mutagen.File(fileobj=stream, easy=True)
    tag: Dict[str, List[str]] = parse_tag(file)
    print(tag)
    strip_tag(file)
    stream.seek(0)
    save_with_no_padding(file=file, destination_stream=stream)
    return MutagenParse.from_tags(tag)


HASH_CHUNK_SIZE = 8192


def hash_file(stream: IO[bytes]) -> hashlib.sha512:
    h = hashlib.sha512()
    stream.seek(0)
    while chunk := stream.read(HASH_CHUNK_SIZE):
        h.update(chunk)
    return h


def determine_extension(path: os.PathLike) -> str:
    _, ext = os.path.splitext(path)
    return ext


def determine_filename(stream: IO[bytes], original_path: os.PathLike) -> pathlib.Path:
    filename = hash_file(stream).hexdigest()
    musicdir = pathlib.Path(config["storage.music.dir"])
    extension = determine_extension(original_path)
    return musicdir.joinpath(f"{filename}{extension}")


def guess_mimetypes(original_path: os.PathLike) -> Tuple[Optional[str], Optional[str]]:
    return mimetypes.guess_type(original_path, strict=False)


def find_album_from_tag(session: sqlalchemy.orm.session.Session,
                        mp: MutagenParse) -> Optional[tables.Album]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])

    query = None
    for artist in mp.album.artists:
        subquery = (
            session.query(tables.AlbumInvolvement)
                   .filter(tables.AlbumInvolvement.role == role_artist)
                   .join(tables.Person)
                   .filter(tables.Person.name == artist)
                   .join(tables.Album)
                   .filter(tables.Album.title == mp.album.title)
        )
        if query is None:
            query = subquery
        else:
            query = subquery.filter(tables.AlbumInvolvement.person_id.in_([person.id for person in query.all()]))

    album_involvement: Optional[tables.AlbumInvolvement] = query.one_or_none() if query else None
    if album_involvement:
        return album_involvement.album
    return None


def find_song_from_tag(session: sqlalchemy.orm.session.Session,
                       mp: MutagenParse) -> Optional[tables.Song]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])

    query = None
    for artist in mp.song.artists:
        subquery = (
            session.query(tables.SongInvolvement)
                   .filter(tables.SongInvolvement.role == role_artist)
                   .join(tables.Person)
                   .filter(tables.Person.name == artist)
                   .join(tables.Song)
                   .filter(tables.Song.title == mp.song.title)
                   .join(tables.Album)
                   .filter(tables.Album.title == mp.album.title)
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
                            mp: MutagenParse) -> Tuple[tables.Album, tables.Song]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])
    role_composer = tables.Role.make(session=session, name=config["apps.files.roles.composer"])
    role_performer = tables.Role.make(session=session, name=config["apps.files.roles.performer"])

    album = find_album_from_tag(session=session, mp=mp)
    if album is None:
        album = tables.Album(
            title=mp.album.title
        )
        session.add(album)
        album.involve(
            people=(tables.Person.make(session=session, name=name) for name in mp.album.artists),
            role=role_artist
        )

    song = find_song_from_tag(session=session, mp=mp)
    if song is None:
        song = tables.Song(
            title=mp.song.title,
            year=mp.song.year,
            disc=mp.song.disc_number,
            track=mp.song.track_number,
            album=album,
            genres=[tables.Genre.make(session=session, name=mp.song.genre)] if mp.song.genre else [],
        )
        session.add(song)
        song.involve(
            people=(tables.Person.make(session=session, name=name) for name in mp.song.artists),
            role=role_artist
        )
        song.involve(
            people=(tables.Person.make(session=session, name=name) for name in mp.song.composers),
            role=role_composer
        )
        song.involve(
            people=(tables.Person.make(session=session, name=name) for name in mp.song.performers),
            role=role_performer
        )

    layer.song = song

    return album, song


READ_CHUNK_SIZE = 8192


@celery.task
def process_music(original_path: os.PathLike,
                  uploader_id: Optional[int] = None,
                  *,
                  layer_data: Optional[Dict[str, Any]] = None,
                  generate_entries: bool = False,
                  delete_original: bool = False) -> Tuple[int, int]:

    if layer_data is None:
        layer_data: Dict[str, Any] = {}

    session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    with open(original_path, "rb") as f:
        stream = io.BytesIO()
        while data := f.read(READ_CHUNK_SIZE):
            stream.write(data)

    mp: MutagenParse = process_tags(stream=stream)
    destination = determine_filename(stream=stream, original_path=original_path)
    mime_type, mime_software = guess_mimetypes(original_path=original_path)

    file: Optional[tables.File] = None
    if os.path.exists(destination):
        file = session.query(tables.File).filter_by(name=str(destination)).one_or_none()
    else:
        with open(destination, "wb") as f:
            while data := stream.read(READ_CHUNK_SIZE):
                f.write(data)
        if delete_original:
            os.remove(original_path)

    if file is None:
        file = tables.File(
            name=str(destination),
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
        album, song = make_entries_from_layer(session=session, layer=layer, mp=mp)
        session.add(album)
        session.add(song)

    session.commit()

    result = (file.id, layer.id)

    session.close()

    return result


__all__ = (
    "process_music",
)
