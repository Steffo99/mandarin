from royalnet.typing import *
import fastapi as f
import hashlib
import os
import mutagen
import io
import sqlalchemy.orm.session
import copy

from ...config import *
from ...database import *
from ...exc import *
from ..utils.auth import *


router_upload = f.APIRouter()


class SHA512CollisionError(MandarinException):
    pass


def save_file(file: f.UploadFile) -> Tuple[str, dict]:
    # Find the file extension
    _, ext = os.path.splitext(file.filename)

    # Parse the audio file
    mutated: mutagen.File = mutagen.File(fileobj=file.file, easy=True)

    # Create a copy of the tags dictionary
    tags: dict = copy.deepcopy(mutated.tags)

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
        raise SHA512CollisionError("A file with that name already exists.")

    # Create the required directories
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save the file
    with open(filename, "wb") as result:
        while chunk := file.file.read(8192):
            result.write(chunk)

    return filename, tags


def song_involve(session: sqlalchemy.orm.session.Session, song: Song, role_name: str, tag_value: str):
    # Ensure the song role exists
    role = (
        session.query(SongRole)
               .filter(SongRole.name == role_name)
               .one_or_none()
    )

    # Create the song role
    if role is None:
        role = SongRole(name=role_name)
        session.add(role)

    # Involve the people with the song
    artists_names = parse_multitag(tag_value)

    # Try to find the people
    for artist_name in artists_names:
        artist = (
            session.query(Person)
                   .filter(Person.name.ilike(artist_name))
                   .one_or_none()
        )

        # Create a new artist
        if artist is None:
            artist = Person(name=artist_name)
            session.add(artist)

        # Involve the artist with the song
        song_involvement = SongInvolvement(person=artist, song=song, role=role)
        session.add(song_involvement)


def parse_multitag(tag: str) -> List[str]:
    stripped_tag = tag.strip()
    if stripped_tag == "":
        return []
    else:
        return [item.strip() for item in stripped_tag.split("/")]


@router_upload.post("/auto/singlelayer")
def auto_singlelayer(user: User = f.Depends(find_or_create_user), file: f.UploadFile = f.File(...)):
    """Upload a single-layer audio track."""
    # TODO: cambiare tutti gli ILIKE

    if file.file is None:
        raise f.HTTPException(500, "'file' was unexpectedly None")

    try:
        filename, tags = save_file(file)
    except SHA512CollisionError:
        raise f.HTTPException(422, "That file was already uploaded.")

    def first_tag(tag: str, default=None):
        value = tags.get(tag)
        if value is None:
            return default
        if len(value) == 0:
            return default
        return value[0].strip()

    # Set the session to REPEATABLE READ mode
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    album_title = first_tag("album")
    album_artists_names = parse_multitag(first_tag("albumartist", ""))

    # If the album has a title...
    if album_title:

        # Ensure the "Artist" album role exists
        album_artist_role = (
            session.query(AlbumRole)
                   .filter(AlbumRole.name == "Artist")
                   .one_or_none()
        )

        # Create the "Artist" album role
        if album_artist_role is None:
            album_artist_role = AlbumRole(name="Artist")
            session.add(album_artist_role)

        # Search for an album + role + artists match
        album: Optional[Album] = (
            session.query(Album)
                   .filter(Album.title.ilike(album_title))
                   .join(AlbumInvolvement)
                   .filter(AlbumInvolvement.role == album_artist_role)
                   .join(Person)
                   .filter(*[Person.name.ilike(artist_name) for artist_name in album_artists_names])
                   .one_or_none()
        )

        # Create a new album if possible
        if album is None:
            album = Album(title=album_title)
            session.add(album)

            # Try to find the artists
            for artist_name in album_artists_names:
                artist = (
                    session.query(Person)
                           .filter(Person.name.ilike(artist_name))
                           .one_or_none()
                )

                # Create a new artist
                if artist is None:
                    artist = Person(name=artist_name)
                    session.add(artist)

                # Involve the artist with the album
                album_involvement = AlbumInvolvement(person=artist, album=album, role=album_artist_role)
                session.add(album_involvement)

    # If the album DOES NOT have a title
    else:
        album = None

    # Create and associate genres
    genre_name = first_tag("genre")

    if genre_name:
        genre = (
            session.query(MusicGenre)
                   .filter(MusicGenre.name.ilike(genre_name))
                   .one_or_none()
        )

        if genre is None:
            genre = MusicGenre(name=genre_name)
            session.add(genre)

        genres = [genre]
    else:
        genres = []

    # Create the new song
    song = Song(
        title=first_tag("title"),
        album=album,
        year=first_tag("date"),
        disc_number=first_tag("discnumber"),
        track_number=first_tag("tracknumber"),
        genres=genres,
    )

    # Involve artists, composers and performer
    song_involve(session=session, song=song, role_name="Artist", tag_value=first_tag("artist", ""))
    song_involve(session=session, song=song, role_name="Composer", tag_value=first_tag("composer", ""))
    song_involve(session=session, song=song, role_name="Performer", tag_value=first_tag("performer", ""))

    # Create the layer
    layer = SongLayer(song=song, filename=filename)
    session.add(layer)

    session.commit()

    return "Success!"


__all__ = (
    "router_upload",
)
