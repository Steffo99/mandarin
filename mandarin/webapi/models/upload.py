from typing import List, Optional
import pydantic

from mandarin.database import *


class UploadFile(File.pydantic()):
    """Information about the file that was uploaded and stored in Mandarin."""


class UploadPerson(Person.pydantic()):
    """A person that was involved with the uploaded song or album."""


class UploadGenre(MusicGenre.pydantic()):
    """The music genre of the uploaded song or album."""


class UploadSongRole(SongRole.pydantic()):
    """The role with which a person was involved with the uploaded song."""


class UploadAlbumRole(AlbumRole.pydantic()):
    """The role with which a person was involved with the uploaded album."""


class UploadAlbumInvolvement(AlbumInvolvement.pydantic()):
    """The involvement of a specific person, having a role ("Artist"), with the uploaded album."""
    person: UploadPerson
    role: UploadAlbumRole


class UploadAlbum(Album.pydantic()):
    """The album that was created during the upload, or that was associated with the new layer."""
    genres: List[UploadGenre]
    involvements: List[UploadAlbumInvolvement]


class UploadSongInvolvement(SongInvolvement.pydantic()):
    """The involvement of a specific person, having a role ("Artist"), with the uploaded song."""
    person: UploadPerson
    role: UploadSongRole


class UploadSong(Song.pydantic()):
    """The song that was created during the upload, or that was associated with the new layer."""
    album: Optional[UploadAlbum]
    involvements: List[UploadSongInvolvement]
    genres: List[UploadGenre]


class UploadLayer(SongLayer.pydantic()):
    """The layer that was created during the upload."""
    song: UploadSong
    file: Optional[UploadFile]


class UploadResult(pydantic.BaseModel):
    """The result of the upload of a track to Mandarin."""
    layer: UploadLayer


__all__ = (
    "UploadFile",
    "UploadPerson",
    "UploadGenre",
    "UploadSongRole",
    "UploadAlbumRole",
    "UploadAlbumInvolvement",
    "UploadAlbum",
    "UploadSongInvolvement",
    "UploadSong",
    "UploadLayer",
    "UploadResult",
)
