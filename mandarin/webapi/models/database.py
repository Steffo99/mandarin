from typing import List, Optional, Type, Container
import pydantic
import pydantic_sqlalchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

from ...database import *


# Copied from pydantic_sqlalchemy
def sqlalchemy_to_pydantic(
    db_model: Type, config: Type, exclude: Optional[Container[str]] = None
) -> Type[pydantic.BaseModel]:
    if exclude is None:
        exclude = []
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Optional[type] = None
                if hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)
    pydantic_model = pydantic.create_model(
        config.title, __config__=config, **fields  # type: ignore
    )
    return pydantic_model


def make_default_model(table):
    class Config(pydantic.BaseConfig):
        orm_mode = True
        title = f"M{table.__name__}"
    return sqlalchemy_to_pydantic(table, config=Config)


def make_model_without_id(table):
    class Config(pydantic.BaseConfig):
        orm_mode = True
        title = f"M{table.__name__}WithoutId"
    return sqlalchemy_to_pydantic(table, config=Config, exclude=["id"])


MAlbumInvolvement = make_default_model(AlbumInvolvement)
MRole = make_default_model(Role)
MAlbum = make_default_model(Album)
MFile = make_default_model(File)
MGenre = make_default_model(Genre)
MLayer = make_default_model(Layer)
MPerson = make_default_model(Person)
MSongInvolvement = make_default_model(SongInvolvement)
MSong = make_default_model(Song)
MUser = make_default_model(User)
MAuditLog = make_default_model(AuditLog)

MAlbumInvolvementWithoutId = make_model_without_id(AlbumInvolvement)
MRoleWithoutId = make_model_without_id(Role)
MAlbumWithoutId = make_model_without_id(Album)
MFileWithoutId = make_model_without_id(File)
MGenreWithoutId = make_model_without_id(Genre)
MLayerWithoutId = make_model_without_id(Layer)
MPersonWithoutId = make_model_without_id(Person)
MSongInvolvementWithoutId = make_model_without_id(SongInvolvement)
MSongWithoutId = make_model_without_id(Song)


class MFileWithUploader(MFile):
    """
    A file stored in Mandarin, including the uploader of the file.
    """
    uploader: MUser


class MFileFull(MFile):
    """
    A file stored in Mandarin, including the uploader of the file, and the places where the file is currently used in.
    """
    uploader: MUser
    used_as_layer: List[MLayer]
    used_as_album_cover: List[MAlbum]


class MAlbumInvolvementFromAlbum(MAlbumInvolvement):
    """
    The involment of a person in an album, including the person and the role of the involvement.
    """
    person: MPerson
    role: MRole


class MAlbumInvolvementFromPerson(MAlbumInvolvement):
    """
    The involment of a person in an album, including the album and the role of the involvement.
    """
    album: MAlbum
    role: MRole


class MAlbumInvolvementFromRole(MAlbumInvolvement):
    """
    The involment of a person in an album, including the person and the album of the involvement.
    """
    person: MPerson
    album: MAlbum


class MSongInvolvementFromSong(MSongInvolvement):
    """
    The involment of a person in a song, including the person and the role of the involvement.
    """
    person: MPerson
    role: MRole


class MSongInvolvementFromPerson(MSongInvolvement):
    """
    The involment of a person in a song, including the song and the role of the involvement.
    """
    song: MSong
    role: MRole


class MSongInvolvementFromRole(MSongInvolvement):
    """
    The involment of a person in a song, including the person and the song of the involvement.
    """
    person: MPerson
    song: MSong


class MRoleFull(MRole):
    """
    A role that people can have in an album or a song, detailing where the role is used.
    """
    album_involvements: List[MAlbumInvolvementFromRole]
    song_involvements: List[MSongInvolvementFromRole]


class MSongBatch(MSong):
    """
    The properties for a song, and its album.
    """
    album: Optional[MAlbum]


class MSongFromLayer(MSong):
    """
    All the properties for a song, except the layers.
    """
    album: Optional[MAlbum]
    involvements: List[MSongInvolvementFromSong]
    genres: List[MGenre]


class MSongFromAlbum(MSong):
    """
    All the properties for a song, except the album.
    """
    layers: List[MLayer]
    involvements: List[MSongInvolvementFromSong]
    genres: List[MGenre]


class MSongFull(MSong):
    """
    All properties for a song.
    """
    layers: List[MLayer]
    album: Optional[MAlbum]
    involvements: List[MSongInvolvementFromSong]
    genres: List[MGenre]


class MLayerFromSong(MLayer):
    """
    A song layer, and its file.
    """
    file: MFile


class MLayerBatch(MLayer):
    """
    A song layer, and non-recursive data about its song.
    """
    song: MSong


class MLayerFromFile(MLayer):
    """
    A song layer, and data about its song.
    """
    song: MSongFromLayer


class MLayerFull(MLayer):
    """
    All properties for a layer.
    """
    song: MSongFromLayer
    file: MFile


class MAlbumFromSong(MAlbum):
    """
    All properties for an album, except its songs.
    """
    involvements: List[MAlbumInvolvementFromAlbum]
    genres: List[MGenre]
    cover: Optional[MFile]


class MAlbumFull(MAlbum):
    """
    All properties for an album.
    """
    involvements: List[MAlbumInvolvementFromAlbum]
    songs: List[MSong]
    genres: List[MGenre]
    cover: Optional[MFile]


class MPersonFull(MPerson):
    """
    All properties for a person.
    """
    song_involvements: List[MSongInvolvementFromPerson]
    album_involvements: List[MAlbumInvolvementFromPerson]


class MGenreAlbums(MGenre):
    """
    Albums having a genre.
    """
    albums: List[MAlbum]


class MGenreSongs(MGenre):
    """
    Songs having a genre.
    """
    songs: List[MSong]


class MGenreFull(MGenre):
    """
    Both albums and songs having a genre.
    """
    albums: List[MAlbum]
    songs: List[MSong]


__all__ = (
    "MAlbumInvolvement",
    "MRole",
    "MAlbum",
    "MFile",
    "MGenre",
    "MLayer",
    "MPerson",
    "MSongInvolvement",
    "MSong",
    "MUser",
    "MAuditLog",
    "MAlbumInvolvementWithoutId",
    "MRoleWithoutId",
    "MAlbumWithoutId",
    "MFileWithoutId",
    "MGenreWithoutId",
    "MLayerWithoutId",
    "MPersonWithoutId",
    "MSongInvolvementWithoutId",
    "MSongWithoutId",
    "MFileWithUploader",
    "MFileFull",
    "MAlbumInvolvementFromAlbum",
    "MAlbumInvolvementFromPerson",
    "MAlbumInvolvementFromRole",
    "MSongInvolvementFromSong",
    "MSongInvolvementFromPerson",
    "MSongInvolvementFromRole",
    "MRoleFull",
    "MSongBatch",
    "MLayerFromFile",
    "MSongFromLayer",
    "MSongFromAlbum",
    "MSongFull",
    "MLayerFromSong",
    "MLayerFull",
    "MLayerBatch",
    "MAlbumFromSong",
    "MAlbumFull",
    "MPersonFull",
    "MGenreAlbums",
    "MGenreSongs",
    "MGenreFull",
)
