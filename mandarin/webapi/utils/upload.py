from __future__ import annotations
from royalnet.typing import *
import hashlib
import mutagen
import os
import fastapi
import sqlalchemy.orm
import royalnet.alchemist as a

from ...config import *
from ...database import *
from ..models.parse import *


def hash_file(file: IO[bytes]) -> hashlib.sha512:
    """
    Calculate the SHA512 hash of a file-like object.
    """

    file.seek(0)

    h = hashlib.sha512()
    while chunk := file.read(8192):
        h.update(chunk)

    return h


def split_file_tags(file: IO[bytes]) -> ParseData:
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
    parse: ParseData = ParseData.from_tags(mutated.tags)

    # Clear all tags
    mutated.delete(fileobj=file)

    return parse


def determine_filename(file: fastapi.UploadFile) -> str:
    # Calculate the hash of the file object
    h = hash_file(file.file)

    # Determine the new filename
    _, ext = os.path.splitext(file.filename)

    # Return the path
    return os.path.join(config["storage.music.dir"], f"{h.hexdigest()}{ext}")


def save_uploadfile(upload_file: fastapi.UploadFile, uploader: User, overwrite: bool = False) -> Tuple[ParseData, File]:
    """
    Parse a UploadFile with mutagen, then store it in the music directory.
    """

    # Split the tags from the file
    data = split_file_tags(upload_file.file)

    # Create a new File object
    file = File.guess(determine_filename(upload_file), uploader=uploader)

    # Ensure a file with that hash doesn't exist
    if not os.path.exists(file.name) or overwrite:

        # Create the required directories
        os.makedirs(os.path.dirname(file.name), exist_ok=True)

        # Save the file
        with open(file.name, "wb") as result:
            while chunk := upload_file.file.read(8192):
                result.write(chunk)

    return data, file


def auto_album(session: sqlalchemy.orm.session.Session, parse_album: ParseAlbum) -> Album:
    """
    Get the album of the parsed song, or create it and add it to the session if it doesn't exist.

    To match the metadata to the Album row,
    """
    artist_arole = AlbumRole.make(session, config["apps.files.roles.album.artist"])

    # Find the album, if it already exists
    query = None
    for artist in parse_album.artists:
        subquery = (
            session.query(AlbumInvolvement)
                   .filter(AlbumInvolvement.role == artist_arole)
                   .join(Person)
                   .filter(Person.name == artist)
                   .join(Album)
                   .filter(Album.title == parse_album.title)
        )

        if query is None:
            query = subquery
        else:
            query = subquery.filter(AlbumInvolvement.person.in_(query.subquery()))
    album_involvement: Optional[AlbumInvolvement] = query.one_or_none() if query else None

    # Create a new album if needed
    if album_involvement is None:
        album = Album(title=parse_album.title)
        session.add(album)

        album.involve(people=(Person.make(session=session, name=name) for name in parse_album.artists),
                      role=artist_arole)
    else:
        album = album_involvement.album

    return album


def auto_song(session: sqlalchemy.orm.session.Session, parse: ParseData) -> Song:
    """
    Get the song of the parsed song, or create it and add it to the session if it doesn't exist.

    Note that this uses **only** the title and the artists
    """

    # Make the necessary SongRoles
    artist_srole = SongRole.make(session=session, name=config["apps.files.roles.song.artist"])
    composer_srole = SongRole.make(session=session, name=config["apps.files.roles.song.composer"])
    performer_srole = SongRole.make(session=session, name=config["apps.files.roles.song.performer"])

    # Find the song, if it already exists
    query = None
    for artist in parse.song.artists:
        subquery = (
            session.query(SongInvolvement)
                   .filter(SongInvolvement.role == artist_srole)
                   .join(Person)
                   .filter(Person.name == artist)
                   .join(Song)
                   .filter(Song.title == parse.song.title)
                   .join(Album)
                   .filter(Album.title == parse.album.title)
        )

        if query is None:
            query = subquery
        else:
            query = subquery.filter(SongInvolvement.person.in_(query.subquery()))

    song_involvement: SongInvolvement = query.one_or_none() if query else None

    # Create a new song if needed
    if song_involvement is None:
        song = Song(
            title=parse.song.title,
            year=parse.song.year,
            disc_number=parse.song.disc_number,
            track_number=parse.song.track_number,
            album=auto_album(session=session, parse_album=parse.album) if parse.album.title else None,
            genres=[MusicGenre.make(session=session, name=parse.song.genre)] if parse.song.genre else [],
        )
        session.add(song)

        # Involve artists
        song.involve(people=(Person.make(session=session, name=name) for name in parse.song.artists),
                     role=artist_srole)

        # Involve composers
        song.involve(people=(Person.make(session=session, name=name) for name in parse.song.composers),
                     role=composer_srole)

        # Involve performers
        song.involve(people=(Person.make(session=session, name=name) for name in parse.song.performers),
                     role=performer_srole)
    else:
        song = song_involvement.song

    return song


__all__ = (
    "hash_file",
    "split_file_tags",
    "determine_filename",
    "save_uploadfile",
    "auto_album",
    "auto_song",
)
