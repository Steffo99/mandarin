from royalnet.typing import *
import sqlalchemy.orm
import fastapi as f

from ...database import *
from ..models.database import *
from ..dependencies import *

router_metadata = f.APIRouter()


@router_metadata.put(
    "/move/layers",
    summary="Move layers to a different song.",
    response_model=List[MLayerFull],
    responses={
        **login_error,
        404: {"description": "Song / layer not found"}
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

    changed_layers = []
    for layer_id in layer_ids:
        layer = session.query(Layer).get(layer_id)
        if layer is None:
            raise f.HTTPException(404, f"The id '{layer_id}' does not match any layer.")

        layer.song = song

        changed_layers.append(MLayerFull.from_orm(layer))
    session.commit()

    return changed_layers


@router_metadata.put(
    "/move/songs",
    summary="Move songs to a different album.",
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


@router_metadata.post(
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


@router_metadata.post(
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


@router_metadata.delete(
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


@router_metadata.delete(
    "/involve/song",
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

        result.append(MSongFull.from_orm(song))
    session.commit()

    return result


@router_metadata.put(
    "/edit/albumrole",
    summary="Edit an album role.",
    response_model=MAlbumRole,
    responses={
        **login_error,
        404: {"description": "Role not found"}
    }
)
def edit_albumrole(
    model: MAlbumRole = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(AlbumRole).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any album role.")

    obj.update(**model.__dict__)
    session.commit()

    return MAlbumRole.from_orm(obj)


@router_metadata.put(
    "/edit/songrole",
    summary="Edit a song role.",
    response_model=MSongRole,
    responses={
        **login_error,
        404: {"description": "Role not found"}
    }
)
def edit_songrole(
    model: MSongRole = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(SongRole).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any song role.")

    obj.update(**model.__dict__)
    session.commit()

    return MSongRole.from_orm(obj)


@router_metadata.put(
    "/edit/album",
    summary="Edit an album.",
    response_model=MAlbum,
    responses={
        **login_error,
        404: {"description": "Album not found"}
    }
)
def edit_album(
    model: MAlbum = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(Album).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any album.")

    obj.update(**model.__dict__)
    session.commit()

    return MAlbum.from_orm(obj)


@router_metadata.put(
    "/edit/genre",
    summary="Edit a genre.",
    response_model=MGenre,
    responses={
        **login_error,
        404: {"description": "Genre not found"}
    }
)
def edit_genre(
    model: MGenre = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(Genre).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any genre.")

    obj.update(**model.__dict__)
    session.commit()

    return MGenre.from_orm(obj)


@router_metadata.put(
    "/edit/layer",
    summary="Edit a layer.",
    response_model=MLayer,
    responses={
        **login_error,
        404: {"description": "Layer not found"}
    }
)
def edit_layer(
    model: MLayer = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(Layer).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any layer.")

    obj.update(**model.__dict__)
    session.commit()

    return MLayer.from_orm(obj)


@router_metadata.put(
    "/edit/person",
    summary="Edit a person.",
    response_model=MPerson,
    responses={
        **login_error,
        404: {"description": "Person not found"}
    }
)
def edit_person(
    model: MPerson = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(Person).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any person.")

    obj.update(**model.__dict__)
    session.commit()

    return MPerson.from_orm(obj)


@router_metadata.put(
    "/edit/song",
    summary="Edit a song.",
    response_model=MSong,
    responses={
        **login_error,
        404: {"description": "Role not found"}
    }
)
def edit_song(
    model: MSong = f.Body(...),
    user: User = f.Depends(dependency_valid_user),
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
):
    obj = session.query(Song).get(model.id)
    if obj is None:
        raise f.HTTPException(404, f"The id '{model.id}' does not match any song.")

    obj.update(**model.__dict__)
    session.commit()

    return MSong.from_orm(obj)



__all__ = (
    "router_metadata",
)
