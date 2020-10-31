from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import hashlib
import os
import mutagen
import sqlalchemy.orm.session
import copy
import dataclasses

from ...config import *
from ...database import *
from ...exc import FileAlreadyExistsError
from ..utils.auth import *


router_upload = f.APIRouter()


def save_file(file: f.UploadFile) -> Tuple[str, mutagen.Tags]:
    """
    Parse a UploadFile with mutagen, then store it in the music directory.

    :param file: The UploadFile to store.
    :return: The name of the resulting file, and its tags.
    """

    # Find the file extension
    _, ext = os.path.splitext(file.filename)

    # Parse the audio file
    mutated: mutagen.File = mutagen.File(fileobj=file.file, easy=True)

    # Create a copy of the tags dictionary
    tags: mutagen.Tags = copy.deepcopy(mutated.tags)

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
    filename = os.path.join(config["storage.music.dir"], f"{h.hexdigest()}{ext}")

    # Ensure a file with that hash doesn't exist
    if os.path.exists(filename):
        raise FileAlreadyExistsError("A file with that name already exists.")

    # Create the required directories
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save the file
    with open(filename, "wb") as result:
        while chunk := file.file.read(8192):
            result.write(chunk)

    return filename, tags


def album_involve(session: sqlalchemy.orm.session.Session, album: Album, role_name: str, people_names: List[str]) -> \
        List[AlbumInvolvement]:
    """Involve a list of people with an album."""
    # Ensure the song role exists
    arole = get_arole(session=session, name=role_name)

    # Create a list containing the involvements that will be returned
    involvements = []

    # Try to find the people
    for person_name in people_names:
        person = get_person(session=session, name=person_name)

        # Involve the artist with the song
        involvement = AlbumInvolvement(person=person, album=album, role=arole)
        session.add(involvement)

        # Add the involvement to the list
        involvements.append(involvement)

    return involvements


def song_involve(session: sqlalchemy.orm.session.Session, song: Song, role_name: str, people_names: List[str]) -> \
        List[SongInvolvement]:
    """Involve a list of people with a song."""
    # Ensure the song role exists
    srole = get_srole(session=session, name=role_name)

    # Create a list containing the involvements that will be returned
    involvements = []

    # Try to find the people
    for person_name in people_names:
        person = get_person(session=session, name=person_name)

        # Involve the artist with the song
        involvement = SongInvolvement(person=person, song=song, role=srole)
        session.add(involvement)

        # Add the involvement to the list
        involvements.append(involvement)

    return involvements


def ieq(one, two):
    """Create a case-insensitive equality filter for SQLAlchemy."""
    return sqlalchemy.func.lower(one) == sqlalchemy.func.lower(two)


def ineq(one, two):
    """Create a case-insensitive inequality filter for SQLAlchemy."""
    return sqlalchemy.func.lower(one) != sqlalchemy.func.lower(two)


@dataclasses.dataclass()
class ParseAlbum:
    title: str
    artists: List[str]

    @classmethod
    def from_tags(cls, tags: mutagen.Tags) -> ParseAlbum:
        return cls(
            title=Parse.single(tags=tags, key="album"),
            artists=Parse.multi(tags=tags, key="albumartists")
        )


@dataclasses.dataclass()
class ParseSong:
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


@dataclasses.dataclass()
class Parse:
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

    @classmethod
    def from_tags(cls, tags: mutagen.Tags):
        return cls(
            album=ParseAlbum.from_tags(tags),
            song=ParseSong.from_tags(tags)
        )


def get_srole(session: sqlalchemy.orm.session.Session, name: str) -> SongRole:
    """Get the SongRole with the specified name, or create one and add it to the session."""
    role = (
        session.query(SongRole)
            .filter(SongRole.name == name)
            .one_or_none()
    )

    if role is None:
        role = SongRole(name=name)
        session.add(role)

    return role


def get_arole(session: sqlalchemy.orm.session.Session, name: str) -> AlbumRole:
    """Get the AlbumRole with the specified name, or create one and add it to the session."""
    role = (
        session.query(AlbumRole)
               .filter(AlbumRole.name == name)
               .one_or_none()
    )

    if role is None:
        role = AlbumRole(name=name)
        session.add(role)

    return role


def get_person(session: sqlalchemy.orm.session.Session, name: str) -> Person:
    """Get the Person with the specified name, or create one and add it to the session."""
    role = (
        session.query(Person)
               .filter(ieq(Person.name, name))
               .one_or_none()
    )

    if role is None:
        role = Person(name=name)
        session.add(role)

    return role


@router_upload.post("/auto/singlelayer")
def auto_singlelayer(user: User = f.Depends(find_or_create_user), file: f.UploadFile = f.File(...)):
    """Upload a single-layer audio track."""

    if file.file is None:
        raise f.HTTPException(500, "No file was uploaded")

    try:
        filename, tags = save_file(file)
    except FileAlreadyExistsError:
        raise f.HTTPException(422, "The file was already uploaded.")

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Make shortcuts for tags_single and tags_multi
    p: Parse = Parse.from_tags(tags=tags)

    # If the album has a title...
    if p.album.title:
        artist_arole = get_arole(session, config["apps.files.roles.album.artist"])

        # Search for an album + role + artists match
        album: Optional[Album] = (
            session.query(Album)
                   .filter(ieq(Album.title, p.album.title))
                   .join(AlbumInvolvement)
                   .filter(AlbumInvolvement.role == artist_arole)
                   .join(Person)
                   .filter(*[ieq(Person.name, artist) for artist in p.album.artists])
                   .one_or_none()
        )

        # Create a new album if possible
        if album is None:
            album = Album(title=p.album.title)
            session.add(album)

            album_involve(session=session,
                          album=album,
                          role_name=config["apps.files.roles.album.artist"],
                          people_names=p.album.artists)

    # If the album DOES NOT have a title
    else:
        album = None

    # Create and associate genres
    if p.song.genre:
        genre = (
            session.query(MusicGenre)
                   .filter(ieq(MusicGenre.name, p.song.genre))
                   .one_or_none()
        )

        if genre is None:
            genre = MusicGenre(name=p.song.genre)
            session.add(genre)

        genres = [genre]
    else:
        genres = []

    # Create the new song
    song = Song(
        title=p.song.title,
        year=p.song.year,
        disc_number=p.song.disc_number,
        track_number=p.song.track_number,
        album=album,
        genres=genres,
    )

    # Involve artists, composers and performer
    song_involve(session=session,
                 song=song,
                 role_name=config["apps.files.roles.album.artist"],
                 people_names=p.song.artists)
    song_involve(session=session,
                 song=song,
                 role_name=config["apps.files.roles.album.composer"],
                 people_names=p.song.composers)
    song_involve(session=session,
                 song=song,
                 role_name=config["apps.files.roles.album.performer"],
                 people_names=p.song.performers)

    # Create the layer
    layer = SongLayer(song=song, filename=filename, uploader=user)
    session.add(layer)

    session.commit()
    session.close()

    return "Success!"


__all__ = (
    "router_upload",
)
