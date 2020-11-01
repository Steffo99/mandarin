from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import hashlib
import os
import mutagen
import sqlalchemy.orm.session
import pydantic
import royalnet.alchemist as a

from ...config import *
from ...database import *
from ..utils.auth import *


router_upload = f.APIRouter()


class ParseAlbum(pydantic.BaseModel):
    """Information about the album of a parsed audio file."""
    title: str
    artists: List[str]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseAlbum:
        """Create a new Parse object from a mutagen.Tags object."""
        return cls(
            title=Parse.single(tags=tags, key="album"),
            artists=Parse.multi(tags=tags, key="albumartists")
        )


class ParseSong(pydantic.BaseModel):
    """Information about the song of a parsed audio file."""
    genre: str
    title: str
    year: int
    disc_number: int
    track_number: int
    artists: List[str]
    composers: List[str]
    performers: List[str]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseSong:
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


class Parse(pydantic.BaseModel):
    """Information about a parsed audio file."""
    filename: Optional[str]
    album: ParseAlbum
    song: ParseSong

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


def save_file(file: f.UploadFile, overwrite: bool = False) -> Parse:
    """
    Parse a UploadFile with mutagen, then store it in the music directory.

    :param file: The UploadFile to store.
    :param overwrite: Overwrite the file instead of skipping if it already exists.
    :return: The parsing result.
    """

    # Find the file extension
    _, ext = os.path.splitext(file.filename)

    # Parse the audio file
    mutated: mutagen.File = mutagen.File(fileobj=file.file, easy=True)

    # Create a Parse object from the tags
    # The filename will be set later
    parse: Parse = Parse(album=ParseAlbum.from_tags(mutated.tags),
                         song=ParseSong.from_tags(mutated.tags),
                         filename=None)

    # Seek back to the beginning
    file.file.seek(0)

    # Clear all tags
    mutated.delete(fileobj=file.file)

    # Seek back to the beginning
    file.file.seek(0)

    # Calculate the hash of the file object
    h = hashlib.sha512()
    while chunk := file.file.read(8192):
        h.update(chunk)

    # Seek back to the beginning
    file.file.seek(0)

    # Find the final filename
    parse.filename = os.path.join(config["storage.music.dir"], f"{h.hexdigest()}{ext}")

    # Ensure a file with that hash doesn't exist
    if not os.path.exists(parse.filename) or overwrite:
        # Create the required directories
        os.makedirs(os.path.dirname(parse.filename), exist_ok=True)

        # Save the file
        with open(parse.filename, "wb") as result:
            while chunk := file.file.read(8192):
                result.write(chunk)

    return parse


def make_album(session: sqlalchemy.orm.session.Session, parse_album: ParseAlbum) -> Album:
    """Get the album of the parsed song, or create it and add it to the session if it doesn't exist."""
    artist_arole = AlbumRole.make(session, config["apps.files.roles.album.artist"])

    # Search for an album + role + artists match
    album: Optional[Album] = (
        session.query(Album)
               .filter(a.ieq(Album.title, parse_album.title))
               .join(AlbumInvolvement)
               .filter(AlbumInvolvement.role == artist_arole)
               .join(Person)
               .filter(*[a.ieq(Person.name, artist) for artist in parse_album.artists])
               .one_or_none()
    )

    # Create a new album if possible
    if album is None:
        album = Album(title=parse_album.title)
        session.add(album)

        album.involve(people=(Person.make(session=session, name=name) for name in parse_album.artists),
                      role=artist_arole)

    return album


def make_song(session: sqlalchemy.orm.session.Session, parse: Parse) -> Song:
    """Get the song of the parsed song, or create it and add it to the session if it doesn't exist."""
    # Create the new song
    song = Song(
        title=parse.song.title,
        year=parse.song.year,
        disc_number=parse.song.disc_number,
        track_number=parse.song.track_number,
        album=make_album(session=session, parse_album=parse.album) if parse.album.title else None,
        genres=[MusicGenre.make(session=session, name=parse.song.genre)] if parse.song.genre else [],
    )
    session.add(song)

    # Involve artists
    song.involve(people=(Person.make(session=session, name=name) for name in parse.song.artists),
                 role=SongRole.make(session=session, name=config["apps.files.roles.song.artist"]))

    # Involve composers
    song.involve(people=(Person.make(session=session, name=name) for name in parse.song.composers),
                 role=SongRole.make(session=session, name=config["apps.files.roles.song.composer"]))

    # Involve performers
    song.involve(people=(Person.make(session=session, name=name) for name in parse.song.performers),
                 role=SongRole.make(session=session, name=config["apps.files.roles.song.performer"]))

    return song


@router_upload.post("/auto/song", summary="Upload a new song.")
def auto(user: User = f.Depends(find_or_create_user), files: List[f.UploadFile] = f.File(...)):
    """
    Upload a new audio track, try to match or create its corresponding metadata database entries.

    The metadata will be based on the first file sent, the metadata of the following files is ignored.
    """

    # Ensure at least a song was uploaded
    if len(files) == 0:
        raise f.HTTPException(500, "No files were uploaded")

    # Parse and save all files
    parses = [save_file(file) for file in files]

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Use the first parse to create the metadata
    song = make_song(session=session, parse=parses[0])

    # Create the layers
    for parse in parses:
        layer = SongLayer(song=song, filename=parse.filename, uploader=user)
        session.add(layer)

    session.commit()
    session.close()


__all__ = (
    "router_upload",
)
