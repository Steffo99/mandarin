from royalnet.typing import *
import sqlalchemy.orm
import fastapi as f

from ..models.upload import *
from ...database import *
from ..utils.auth import *

router_metadata = f.APIRouter()


@router_metadata.put(
    "/move/layers",
    summary="Move layers to a different song.",
    response_model=List[UploadLayer],
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Song / layer not found"}
    }
)
def move_layers(
    layer_ids: List[int] = f.Query(...),
    song_id: int = f.Query(...),
    user: User = f.Depends(find_or_create_user),
):
    session: sqlalchemy.orm.session.Session = Session()

    song = session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

    changed_layers = []
    for layer_id in layer_ids:
        layer = session.query(SongLayer).get(layer_id)
        if layer is None:
            raise f.HTTPException(404, f"The id '{layer_id}' does not match any layer.")

        layer.song = song
        changed_layers.append(UploadLayer.from_orm(layer))

    session.commit()
    session.close()

    return changed_layers


@router_metadata.put(
    "/move/songs",
    summary="Move songs to a different album.",
    response_model=List[UploadSong],
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Album / song not found"}
    }
)
def move_songs(
    song_ids: List[int] = f.Query(...),
    album_id: int = f.Query(...),
    user: User = f.Depends(find_or_create_user),
):
    session: sqlalchemy.orm.session.Session = Session()

    album = session.query(Album).get(album_id)
    if album is None:
        raise f.HTTPException(404, f"The id '{album_id}' does not match any album.")

    changed_songs = []
    for song_id in song_ids:

        song = session.query(Song).get(song_id)
        if song is None:
            raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

        song.album = album
        changed_songs.append(UploadSong.from_orm(song))

    session.commit()
    session.close()

    return changed_songs


@router_metadata.post(
    "/involve/album",
    summary="Involve people with an album.",
    response_model=UploadAlbum,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Album / role / person not found"}
    }
)
def involve_album(
    person_ids: List[int] = f.Query(...),
    album_id: int = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(find_or_create_user),
):
    session: sqlalchemy.orm.session.Session = Session()

    album = session.query(Album).get(album_id)
    if album is None:
        raise f.HTTPException(404, f"The id '{album_id}' does not match any album.")

    role = session.query(AlbumRole).get(role_id)
    if role is None:
        raise f.HTTPException(404, f"The id '{role_id}' does not match any album role.")

    for person_id in person_ids:

        person = session.query(Person).get(person_id)
        if person is None:
            raise f.HTTPException(404, f"The id '{person_id}' does not match any person.")

        involvement = session.query(AlbumInvolvement).filter_by(album=album, role=role, person=person)
        if involvement is None:
            involvement = AlbumInvolvement(album=album, role=role, person=person)
            session.add(involvement)

    session.commit()

    result = UploadAlbum.from_orm(album)

    session.close()

    return result


@router_metadata.post(
    "/involve/song",
    summary="Involve people with a song.",
    response_model=UploadSong,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Song / role / person not found"}
    }
)
def involve_song(
    person_ids: List[int] = f.Query(...),
    song_id: int = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(find_or_create_user),
):
    session: sqlalchemy.orm.session.Session = Session()

    song = session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any album.")

    role = session.query(AlbumRole).get(role_id)
    if role is None:
        raise f.HTTPException(404, f"The id '{role_id}' does not match any album role.")

    for person_id in person_ids:

        person = session.query(Person).get(person_id)
        if person is None:
            raise f.HTTPException(404, f"The id '{person_id}' does not match any person.")

        involvement = session.query(SongInvolvement).filter_by(song=song, role=role, person=person)
        if involvement is None:
            involvement = SongInvolvement(song=song, role=role, person=person)
            session.add(involvement)

    session.commit()

    result = UploadSong.from_orm(song)

    session.close()

    return result


@router_metadata.delete(
    "/involve/album",
    summary="Uninvolve people from an album.",
    response_model=UploadAlbum,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Album / role / person not found"}
    }
)
def uninvolve_album(
    person_ids: List[int] = f.Query(...),
    album_id: int = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(find_or_create_user),
):
    session: sqlalchemy.orm.session.Session = Session()

    album = session.query(Album).get(album_id)
    if album is None:
        raise f.HTTPException(404, f"The id '{album_id}' does not match any album.")

    role = session.query(AlbumRole).get(role_id)
    if role is None:
        raise f.HTTPException(404, f"The id '{role_id}' does not match any album role.")

    for person_id in person_ids:

        person = session.query(Person).get(person_id)
        if person is None:
            raise f.HTTPException(404, f"The id '{person_id}' does not match any person.")

        involvement = session.query(AlbumInvolvement).filter_by(album=album, role=role, person=person)
        if involvement is not None:
            session.delete(involvement)

    session.commit()

    result = UploadAlbum.from_orm(album)

    session.close()

    return result


@router_metadata.delete(
    "/involve/song",
    summary="Uninvolve people from a song.",
    response_model=UploadSong,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Song / role / person not found"}
    }
)
def uninvolve_song(
    person_ids: List[int] = f.Query(...),
    song_id: int = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(find_or_create_user),
):
    session: sqlalchemy.orm.session.Session = Session()

    song = session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any album.")

    role = session.query(AlbumRole).get(role_id)
    if role is None:
        raise f.HTTPException(404, f"The id '{role_id}' does not match any album role.")

    for person_id in person_ids:

        person = session.query(Person).get(person_id)
        if person is None:
            raise f.HTTPException(404, f"The id '{person_id}' does not match any person.")

        involvement = session.query(SongInvolvement).filter_by(song=song, role=role, person=person)
        if involvement is not None:
            session.delete(involvement)

    session.commit()

    result = UploadSong.from_orm(song)

    session.close()

    return result




__all__ = (
    "router_metadata",
)
