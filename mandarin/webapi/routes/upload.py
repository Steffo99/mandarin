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
    title: Optional[str]
    artists: List[str]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseAlbum:
        """Create a new Parse object from a mutagen.Tags object."""
        return cls(
            title=ParseData.single(tags=tags, key="album"),
            artists=ParseData.multi(tags=tags, key="albumartists")
        )


class ParseSong(pydantic.BaseModel):
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
    def from_tags(cls, tags: mutagen.Tags) -> ParseSong:
        """Create a new Parse object from a mutagen.Tags object."""
        return cls(
            genre=ParseData.single(tags=tags, key="genre"),
            title=ParseData.single(tags=tags, key="title"),
            year=ParseData.integer(tags=tags, key="date"),
            disc_number=ParseData.integer(tags=tags, key="discnumber"),
            track_number=ParseData.integer(tags=tags, key="tracknumber"),
            artists=ParseData.multi(tags=tags, key="artist"),
            composers=ParseData.multi(tags=tags, key="composer"),
            performers=ParseData.multi(tags=tags, key="performer"),
        )


class ParseData(pydantic.BaseModel):
    """Information about a parsed audio file."""
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
        value = ParseData.single(tags=tags, key=key)

        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            return error

    @staticmethod
    def multi(tags: mutagen.Tags, key: str) -> List[str]:
        """Get all the values (slash-separated) contained inside a specific tag."""
        value = ParseData.single(tags=tags, key=key)

        if value is None:
            return []

        if value == "":
            return []

        else:
            return [item.strip() for item in value.split("/")]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseData:
        return ParseData(
            album=ParseAlbum.from_tags(tags),
            song=ParseSong.from_tags(tags),
            file=None
        )


class ParseResult(pydantic.BaseModel):
    """Information about the results of a file parse."""
    data: ParseData
    file: File


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


def determine_filename(file: f.UploadFile) -> str:
    # Calculate the hash of the file object
    h = hash_file(file.file)

    # Determine the new filename
    _, ext = os.path.splitext(file.filename)

    # Return the path
    return os.path.join(config["storage.music.dir"], f"{h.hexdigest()}{ext}")


def save_uploadfile(upload_file: f.UploadFile, uploader: User, overwrite: bool = False) -> ParseResult:
    """Parse a UploadFile with mutagen, then store it in the music directory."""

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

    return ParseResult(
        file=file,
        data=data,
    )


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


def make_song(session: sqlalchemy.orm.session.Session, parse: ParseData) -> Song:
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
    parses = [save_uploadfile(file, uploader=user) for file in files]

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Use the first parse to create the metadata
    song = make_song(session=session, parse=parses[0].data)

    # Create the layers
    for parse in parses:
        session.add(parse.file)
        layer = SongLayer(song=song, file=parse.file)
        session.add(layer)

    session.commit()
    session.close()


__all__ = (
    "router_upload",
)
