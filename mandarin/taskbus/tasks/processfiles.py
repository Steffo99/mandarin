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


def tag_parse(file: mutagen.File) -> Dict[str, List[str]]:
    """
    Copy the tag of a :class:`mutagen.File` to a :class:`dict`.

    :param file: The file to copy the tags from.
    :return: The copied dict.
    """
    tag: Dict[str, List[str]] = dict(file.tags)
    return tag


def tag_strip(file: mutagen.File) -> None:
    """
    Remove the tag of a :class:`mutagen.File`.

    :param file: The file to remove the tags of.
    """
    file.tags.clear()


def tag_save(file: mutagen.File, destination_stream: IO[bytes]) -> IO[bytes]:
    """
    Write the specified :class:`mutagen.File` to the passed destination stream (which can be any writeable file-like
    object), using no padding for the tag section.

    :param file: The file to save.
    :param destination_stream: The file-like object to save the file to.

                               .. important:: The destination stream must be the same exact one that was used to
                                              create the ``file``, otherwise :mod:`mutagen` won't work!
    """
    file.save(fileobj=destination_stream, padding=lambda _: 0)
    return destination_stream


def tag_process(stream: IO[bytes]) -> MutagenParse:
    """
    Extract the tag of a file from its contents, creating a :class:`.MutagenParse` object.

    :param stream: The file-like object that will be parsed and **edited**.
    :return: The :class:`.MutagenParse` object containing information about the song.
    """
    stream.seek(0)
    file: mutagen.File = mutagen.File(fileobj=stream, easy=True)
    tag: Dict[str, List[str]] = tag_parse(file)
    tag_strip(file)
    stream.seek(0)
    tag_save(file=file, destination_stream=stream)
    return MutagenParse.from_tags(tag)


HASH_CHUNK_SIZE = 8192


def hash_file(stream: IO[bytes]) -> hashlib.sha512:
    """
    Calculate the :class:`hashlib.sha512` hash of a file-like object.

    :param stream: The file-like object to calculate the hash of.
    :return: The :class:`hashlib.sha512` hash.
    """
    h = hashlib.sha512()
    stream.seek(0)
    while chunk := stream.read(HASH_CHUNK_SIZE):
        h.update(chunk)
    return h


def determine_extension(path: os.PathLike) -> str:
    """
    Determine the extension of a file path.

    :param path: The path-like object to parse, such as a :class:`str` or a `pathlib.Path`.
    :return: The extension of the file object.
    """
    _, ext = os.path.splitext(path)
    return ext


def determine_filename(stream: IO[bytes], original_path: os.PathLike) -> pathlib.Path:
    """
    Determine the filename that should be given to a music file, passed as a file-like object.

    :param stream: The file-like object.
    :param original_path: The original path of the file, used to determine the extension and the mimetype.
    :return: A :class:`pathlib.Path` object representing the path that the file should have.
    """
    filename = hash_file(stream).hexdigest()
    musicdir = pathlib.Path(config["storage.music.dir"])
    extension = determine_extension(original_path)
    return musicdir.joinpath(f"{filename}{extension}")


def guess_mimetype(original_path: os.PathLike) -> Tuple[Optional[str], Optional[str]]:
    """
    Try to guess the mimetype and the mimeapplication from a path-like object.

    :param original_path: The path-like object to guess the mimetype from.
    :return: A :class:`tuple` of the mimetype and the mimeapplication. Either can be :data:`None` if the guess failed.
    """
    return mimetypes.guess_type(original_path, strict=False)


def find_album_from_tag(session: sqlalchemy.orm.session.Session,
                        mp: MutagenParse) -> Optional[tables.Album]:
    """
    Try to find in the database the :class:`~mandarin.database.tables.Album` that matches the passed
    :class:`.MutagenParse` object.

    :param session: The :class:`~sqlalchemy.orm.session.Session` to use for the search.
    :param mp: The :class:`.MutagenParse` object.
    :return: The found :class:`~mandarin.database.tables.Album`, or :data:`None` if no matches were found.
    """
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
    """
    Try to find in the database the :class:`~mandarin.database.tables.Song` that matches the passed
    :class:`.MutagenParse` object.

    :param session: The :class:`~sqlalchemy.orm.session.Session` to use for the search.
    :param mp: The :class:`.MutagenParse` object.
    :return: The found :class:`~mandarin.database.tables.Song`, or :data:`None` if no matches were found.
    """
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
    """
    Create :class:`~mandarin.database.tables.Album`, :class:`~mandarin.database.tables.Song`,
    and :class:`~mandarin.database.tables.Person` entries for the specified layer, using the information contained in
    the passed :class:`.MutagenParse`.

    :param session: The :class:`~sqlalchemy.orm.session.Session` to use; all created entries **will be added to it**.
    :param layer: The :class:`~mandarin.database.tables.Layer` to associate the created entities with.
    :param mp: The :class:`.MutagenParse` to source the information from.
    """
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
    """
    A :mod:`celery` task that processes an uploaded music file.

    :param original_path: The temporary path where the file is initially stored.
    :param uploader_id: The id of the :class:`~mandarin.database.tables.User` who uploaded the file, or :data:`None`
                        if it was anonymous.
    :param layer_data: ``**kwargs`` to pass to the :class:`~mandarin.database.tables.Layer` constructor.
    :param generate_entries: Whether entries for the music file should be generated with
                             :func:`.make_entries_from_layer`.
    :param delete_original: If the initial file should be deleted after it is copied to the data directory. Useful
                            for testing, or to import existing media libraries.
    :return: A :class:`tuple` of the ids of the created :class:`~mandarin.database.tables.File` and
             :class:`~mandarin.database.tables.Layer` respectively.
    """

    if layer_data is None:
        layer_data: Dict[str, Any] = {}

    session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    with open(original_path, "rb") as f:
        stream = io.BytesIO()
        while data := f.read(READ_CHUNK_SIZE):
            stream.write(data)

    mp: MutagenParse = tag_process(stream=stream)
    destination = determine_filename(stream=stream, original_path=original_path)
    mime_type, mime_software = guess_mimetype(original_path=original_path)

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
