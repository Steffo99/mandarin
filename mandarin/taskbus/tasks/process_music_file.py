from royalnet.typing import *
import eyed3.core
import eyed3.id3
import eyed3.mp3
import os
import pathlib
import hashlib
import mimetypes
import sqlalchemy.orm

from ..celery import celery
from ...config import config
from ...database import tables, Session


def parse_tag(path: os.PathLike) -> eyed3.core.Tag:
    file: Union[eyed3.id3.TagFile, eyed3.mp3.Mp3AudioFile] = eyed3.core.load(path)
    return file.tag


def strip_tag(path: os.PathLike) -> None:
    file: Union[eyed3.id3.TagFile, eyed3.mp3.Mp3AudioFile] = eyed3.core.load(path)
    file.initTag()


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


def find_album_from_tag(session: sqlalchemy.orm.session.Session, tag: eyed3.core.Tag) -> Optional[tables.Album]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])

    query = None
    for artist in field_list(tag.album_artist):
        subquery = (
            session.query(tables.AlbumInvolvement)
                   .filter(tables.AlbumInvolvement.role == role_artist)
                   .join(tables.Person)
                   .filter(tables.Person.name == artist)
                   .join(tables.Album)
                   .filter(tables.Album.title == field_str(tag.album))
        )
        if query is None:
            query = subquery
        else:
            query = subquery.filter(tables.AlbumInvolvement.person_id.in_([person.id for person in query.all()]))

    album_involvement: Optional[tables.AlbumInvolvement] = query.one_or_none() if query else None
    if album_involvement:
        return album_involvement.album
    return None


def find_song_from_tag(session: sqlalchemy.orm.session.Session, tag: eyed3.core.Tag) -> Optional[tables.Song]:
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])

    query = None
    for artist in field_list(tag.album_artist):
        subquery = (
            session.query(tables.SongInvolvement)
                   .filter(tables.SongInvolvement.role == role_artist)
                   .join(tables.Person)
                   .filter(tables.Person.name == artist)
                   .join(tables.Song)
                   .filter(tables.Song.title == field_str(tag.title))
                   .join(tables.Album)
                   .filter(tables.Album.title == field_str(tag.album))
        )
        if query is None:
            query = subquery
        else:
            query = subquery.filter(tables.SongInvolvement.person_id.in_([person.id for person in query.all()]))

    song_involvement: tables.SongInvolvement = query.one_or_none() if query else None
    if song_involvement:
        return song_involvement.song
    return None


def make_entries_from_file(session: sqlalchemy.orm.session.Session, file: tables.File, tag: eyed3.core.Tag):
    role_artist = tables.Role.make(session=session, name=config["apps.files.roles.artist"])
    role_composer = tables.Role.make(session=session, name=config["apps.files.roles.composer"])
    role_performer = tables.Role.make(session=session, name=config["apps.files.roles.performer"])

    album = find_album_from_tag(session=session, tag=tag)
    if album is None:
        album = tables.Album(
            title=field_str(tag.album)
        )
        session.add(album)
        album.involve(
            people=(tables.Person.make(session=session, name=name) for name in field_list(tag.artist)),
            role=role_artist
        )

    song = find_song_from_tag(session=session, tag=tag)
    if song is None:
        song = tables.Song(
            title=field_str(tag.title),
            year=field_int(tag.),
            disc=parse.song.disc_number,
            track=parse.song.track_number,
            album=auto_album(session=session, parse_album=parse.album) if parse.album.title else None,
            genres=[dt.Genre.make(session=session, name=parse.song.genre)] if parse.song.genre else [],
        )


@celery.task
def process_music(path: os.PathLike, uploader_id: Optional[int] = None):
    tag: eyed3.core.Tag = parse_tag(path)
    strip_tag(path)
    destination = determine_filename(path)
    mime_type, mime_software = guess_mimetypes(path)
    move_file(source=path, destination=destination)

    session = Session()
    file = tables.File(
        name=destination.name,
        mime_type=mime_type,
        mime_software=mime_software,
        uploader_id=uploader_id
    )
    session.add(file)
    session.commit()
