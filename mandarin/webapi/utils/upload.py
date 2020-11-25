from __future__ import annotations
import os
import sqlalchemy.orm
from royalnet.typing import *
import hashlib
import dataclasses
import mutagen
import fastapi

from ...config import config
from ...database import tables as dt


@dataclasses.dataclass()
class Parse:
    """Information about a parsed audio file."""

    @dataclasses.dataclass()
    class Album:
        """Information about the album of a parsed audio file."""
        title: Optional[str]
        artists: List[str]

        @classmethod
        def from_tags(cls, tags: mutagen.Tags) -> Parse.Album:
            """Create a new Parse object from a mutagen.Tags object."""
            return cls(
                title=Parse.single(tags=tags, key="album"),
                artists=Parse.multi(tags=tags, key="albumartists")
            )

    @dataclasses.dataclass()
    class Song:
        """Information about the song of a parsed audio file."""
        genre: Optional[str]
        title: Optional[str]
        year: Optional[int]
        disc_number: Optional[int]
        track_number: Optional[int]
        artists: List[str]
        composers: List[str]
        performers: List[str]

        @classmethod
        def from_tags(cls, tags: mutagen.Tags) -> Parse.Song:
            """Create a new Parse object from a mutagen.Tags object."""
            return cls(
                genre=Parse.single(tags=tags, key="genre"),
                title=Parse.single(tags=tags, key="title"),
                year=Parse.integer(tags=tags, key="date"),
                disc_number=Parse.integer(tags=tags, key="discnumber"),
                track_number=Parse.integer(tags=tags, key="tracknumber"),
                artists=Parse.multi(tags=tags, key="artist"),
                composers=Parse.multi(tags=tags, key="composer"),
                performers=Parse.multi(tags=tags, key="performer"),
            )

    album: Album
    song: Song

    @staticmethod
    def single(tags: mutagen.Tags, key: str, default: Any = None) -> Any:
        """Get the full value contained inside a specific tag."""
        value = tags.get(key)

        if value is None:
            return default

        if len(value) == 0:
            return default

        return value[0].strip()

    @staticmethod
    def integer(tags: mutagen.Tags, key: str, default: Any = None, error: Any = None) -> Any:
        """Get the full value contained inside a specific tag, as int"""
        value = Parse.single(tags=tags, key=key)

        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            return error

    @staticmethod
    def multi(tags: mutagen.Tags, key: str) -> List[str]:
        """Get all the values (slash-separated) contained inside a specific tag."""
        value = Parse.single(tags=tags, key=key)

        if value is None:
            return []

        if value == "":
            return []

        else:
            return [item.strip() for item in value.split("/")]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> Parse:
        return Parse(
            album=Parse.Album.from_tags(tags),
            song=Parse.Song.from_tags(tags),
        )


def hash_file(file: IO[bytes]) -> hashlib.sha512:
    """
    Calculate the SHA512 hash of a file-like object.
    """
    # Seek back to the beginning
    file.seek(0)

    h = hashlib.sha512()
    while chunk := file.read(8192):
        h.update(chunk)

    return h


def split_file_tags(file: IO[bytes]) -> Parse:
    """
    Parse the tags of a file, then strip them from the file object.

    Warning: This affects the file object permanently!
    """
    # Seek back to the beginning
    file.seek(0)

    # Parse the audio file
    mutated: mutagen.File = mutagen.File(fileobj=file, easy=True)

    # Create a Parse object from the tags
    # The file will be set later
    parse: Parse = Parse.from_tags(mutated.tags)

    # Clear all tags
    mutated.delete(fileobj=file)

    return parse


def determine_filename(file: fastapi.UploadFile) -> str:
    """
    Determine the filename of a fastapi.UploadFile
    """
    # Calculate the hash of the file object
    h = hash_file(file.file)

    # Determine the new filename
    _, ext = os.path.splitext(file.filename)

    # Return the path
    return os.path.join(config["storage.music.dir"], f"{h.hexdigest()}{ext}")


def save_uploadfile(upload_file: fastapi.UploadFile, overwrite: bool = False) -> Tuple[Parse, str]:
    """
    Parse a UploadFile with mutagen, then store it in the music directory.
    """

    # Split the tags from the file
    data = split_file_tags(upload_file.file)

    # Find the filename
    filename = determine_filename(upload_file)

    # Ensure a file with that hash doesn't exist
    if not os.path.exists(filename) or overwrite:

        # Create the required directories
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Seek back to the beginning
        upload_file.file.seek(0)

        # Save the file
        with open(filename, "wb") as result:
            while chunk := upload_file.file.read(8192):
                result.write(chunk)

    return data, filename


def auto_album(session: sqlalchemy.orm.session.Session, parse_album: Parse.Album) -> Parse.Album:
    """
    Get the album of the parsed song, or create it and add it to the session if it doesn't exist.

    To match the metadata to the Album row,
    """
    album_artist_role = dt.Role.make(session=session, name=config["apps.files.roles.albumartist"])

    # Find the album, if it already exists
    query = None
    for artist in parse_album.artists:
        subquery = (
            session.query(dt.AlbumInvolvement)
                   .filter(dt.AlbumInvolvement.role == album_artist_role)
                   .join(dt.Person)
                   .filter(dt.Person.name == artist)
                   .join(dt.Album)
                   .filter(dt.Album.title == parse_album.title)
        )

        if query is None:
            query = subquery
        else:
            query = subquery.filter(dt.AlbumInvolvement.person_id.in_([person.id for person in query.all()]))
    album_involvement: Optional[dt.AlbumInvolvement] = query.one_or_none() if query else None

    # Create a new album if needed
    if album_involvement is None:
        album = dt.Album(title=parse_album.title)
        session.add(album)

        album.involve(people=(dt.Person.make(session=session, name=name) for name in parse_album.artists),
                      role=album_artist_role)
    else:
        album = album_involvement.album

    return album


def auto_song(session: sqlalchemy.orm.session.Session, parse: Parse) -> Parse.Song:
    """
    Get the song of the parsed song, or create it and add it to the session if it doesn't exist.

    Note that this uses **only** the title and the artists
    """

    # Make the necessary SongRoles
    artist_role = dt.Role.make(session=session, name=config["apps.files.roles.artist"])
    composer_role = dt.Role.make(session=session, name=config["apps.files.roles.composer"])
    performer_role = dt.Role.make(session=session, name=config["apps.files.roles.performer"])

    # Find the song, if it already exists
    query = None
    for artist in parse.song.artists:
        subquery = (
            session.query(dt.SongInvolvement)
                   .filter(dt.SongInvolvement.role == artist_role)
                   .join(dt.Person)
                   .filter(dt.Person.name == artist)
                   .join(dt.Song)
                   .filter(dt.Song.title == parse.song.title)
                   .join(dt.Album)
                   .filter(dt.Album.title == parse.album.title)
        )

        if query is None:
            query = subquery
        else:
            query = subquery.filter(dt.SongInvolvement.person_id.in_([person.id for person in query.all()]))

    song_involvement: dt.SongInvolvement = query.one_or_none() if query else None

    # Create a new song if needed
    if song_involvement is None:
        song = dt.Song(
            title=parse.song.title,
            year=parse.song.year,
            disc=parse.song.disc_number,
            track=parse.song.track_number,
            album=auto_album(session=session, parse_album=parse.album) if parse.album.title else None,
            genres=[dt.Genre.make(session=session, name=parse.song.genre)] if parse.song.genre else [],
        )
        session.add(song)

        # Involve artists
        song.involve(people=(dt.Person.make(session=session, name=name) for name in parse.song.artists),
                     role=artist_role)

        # Involve composers
        song.involve(people=(dt.Person.make(session=session, name=name) for name in parse.song.composers),
                     role=composer_role)

        # Involve performers
        song.involve(people=(dt.Person.make(session=session, name=name) for name in parse.song.performers),
                     role=performer_role)
    else:
        song = song_involvement.song

    return song


__all__ = (
    "Parse",
    "hash_file",
    "split_file_tags",
    "determine_filename",
    "save_uploadfile",
    "auto_album",
    "auto_song",
)
