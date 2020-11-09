from royalnet.typing import *
import sqlalchemy.orm
import fastapi as f

from mandarin.database import *
from mandarin.webapi.models.database import *
from mandarin.webapi.dependencies import *

router_links = f.APIRouter()


@router_links.patch(
    "/attach/layers_to_song",
    summary="Attach multiple layers to a specific song.",
    response_model=List[MLayerFull],
    responses={
        **login_error,
        404: {"description": "Song not found"}
    }
)
def move_layers(
    layer_ids: List[int] = f.Query(...),
    song_id: int = f.Query(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    song = session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

    layers = session.query(Layer).filter(Layer.id.in_(layer_ids)).all()

    result = []
    for layer in layers:
        layer.song = song
        result.append(MLayerFull.from_orm(layer))
    session.commit()

    return result


@router_links.patch(
    "/attach/album",
    summary="Attach songs to an album.",
    response_model=List[MSongFull],
    responses={
        **login_error,
        404: {"description": "Album / song not found"}
    }
)
def move_songs(
    song_ids: List[int] = f.Query(...),
    album_id: int = f.Query(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    album = session.query(Album).get(album_id)
    if album is None:
        raise f.HTTPException(404, f"The id '{album_id}' does not match any album.")

    result = []
    for song_id in song_ids:

        song = session.query(Song).get(song_id)
        if song is None:
            raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

        song.album = album

        result.append(MSongFull.from_orm(song))
    session.commit()

    return result


@router_links.put(
    "/involve/albums",
    summary="Involve people with albums.",
    response_model=List[MAlbumFull],
    responses={
        **login_error,
        404: {"description": "Album / role / person not found"}
    }
)
def involve_album(
    person_ids: List[int] = f.Query(...),
    album_ids: List[int] = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    result = []
    for album_id in album_ids:

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

        result.append(MAlbumFull.from_orm(album))
    session.commit()

    return result


@router_links.delete(
    "/involve/albums",
    summary="Uninvolve people from albums.",
    response_model=List[MAlbumFull],
    responses={
        **login_error,
        404: {"description": "Album / role / person not found"}
    }
)
def uninvolve_album(
    person_ids: List[int] = f.Query(...),
    album_ids: List[int] = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    result = []
    for album_id in album_ids:

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

        result.append(MAlbumFull.from_orm(album))
    session.commit()

    return result


@router_links.put(
    "/involve/songs",
    summary="Involve people with songs.",
    response_model=List[MSongFull],
    responses={
        **login_error,
        404: {"description": "Song / role / person not found"}
    }
)
def involve_song(
    person_ids: List[int] = f.Query(...),
    song_ids: List[int] = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    result = []
    for song_id in song_ids:

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

        result.append(MSongFull.from_orm(song))
    session.commit()

    return result


@router_links.delete(
    "/involve/songs",
    summary="Uninvolve people from albums.",
    response_model=List[MSongFull],
    responses={
        **login_error,
        404: {"description": "Song / role / person not found"}
    }
)
def uninvolve_song(
    person_ids: List[int] = f.Query(...),
    song_ids: List[int] = f.Query(...),
    role_id: int = f.Query(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    result = []
    for song_id in song_ids:

        song = session.query(Song).get(song_id)
        if song is None:
            raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

        role = session.query(SongRole).get(role_id)
        if role is None:
            raise f.HTTPException(404, f"The id '{role_id}' does not match any song role.")

        for person_id in person_ids:

            person = session.query(Person).get(person_id)
            if person is None:
                raise f.HTTPException(404, f"The id '{person_id}' does not match any person.")

            involvement = session.query(SongInvolvement).filter_by(song=song, role=role, person=person).all()
            if involvement is not None:
                session.delete(involvement)

        result.append(MSongFull.from_orm(song))
    session.commit()

    return result


__all__ = (
    "router_links",
)
