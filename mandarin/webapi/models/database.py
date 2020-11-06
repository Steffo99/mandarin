from typing import List, Optional
import pydantic
import pydantic_sqlalchemy

from ...database import *


MAlbumInvolvement = pydantic_sqlalchemy.sqlalchemy_to_pydantic(AlbumInvolvement)
MAlbumRole = pydantic_sqlalchemy.sqlalchemy_to_pydantic(AlbumRole)
MAlbum = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Album)
MFile = pydantic_sqlalchemy.sqlalchemy_to_pydantic(File)
MGenre = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Genre)
MLayer = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Layer)
MPerson = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Person)
MSongInvolvement = pydantic_sqlalchemy.sqlalchemy_to_pydantic(SongInvolvement)
MSongRole = pydantic_sqlalchemy.sqlalchemy_to_pydantic(SongRole)
MSong = pydantic_sqlalchemy.sqlalchemy_to_pydantic(Song)
MUser = pydantic_sqlalchemy.sqlalchemy_to_pydantic(User)


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
    used_as_layer: MLayer
    used_as_album_cover: MAlbum


class MAlbumInvolvementFromAlbum(MAlbumInvolvement):
    """
    The involment of a person in an album, including the person and the role of the involvement.
    """
    person: MPerson
    role: MAlbumRole


class MAlbumInvolvementFromPerson(MAlbumInvolvement):
    """
    The involment of a person in an album, including the album and the role of the involvement.
    """
    album: MAlbum
    role: MAlbumRole


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
    role: MSongRole


class MSongInvolvementFromPerson(MSongInvolvement):
    """
    The involment of a person in a song, including the song and the role of the involvement.
    """
    song: MSong
    role: MSongRole


class MSongInvolvementFromRole(MSongInvolvement):
    """
    The involment of a person in a song, including the person and the song of the involvement.
    """
    person: MPerson
    song: MSong


class MAlbumRoleFull(MAlbumRole):
    """
    A role that people can have in an album, detailing where the role is used.
    """
    involvements: List[MAlbumInvolvement]


class MSongRoleFull(MSongRole):
    """
    A role that people can have in a song, detailing where the role is used.
    """
    involvements: List[MSongInvolvement]


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
    "MAlbumRole",
    "MAlbum",
    "MFile",
    "MGenre",
    "MLayer",
    "MPerson",
    "MSongInvolvement",
    "MSongRole",
    "MSong",
    "MUser",
    "MFileWithUploader",
    "MFileFull",
    "MAlbumInvolvementFromAlbum",
    "MAlbumInvolvementFromPerson",
    "MAlbumInvolvementFromRole",
    "MSongInvolvementFromSong",
    "MSongInvolvementFromPerson",
    "MSongInvolvementFromRole",
    "MAlbumRoleFull",
    "MSongRoleFull",
    "MSongFromLayer",
    "MSongFromAlbum",
    "MSongFull",
    "MLayerFromSong",
    "MLayerFull",
    "MAlbumFromSong",
    "MAlbumFull",
    "MPersonFull",
    "MGenreAlbums",
    "MGenreSongs",
    "MGenreFull",
)
