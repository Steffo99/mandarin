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


def editable(table_type, input_model, response_model):
    @router_metadata.post(
        f"/table/{table_type.__tablename__}",
        summary=f"Create a new {table_type.__name__}",
        response_model=response_model,
        responses={
            **login_error,
        }
    )
    def post(
        model: input_model = f.Body(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        obj = table_type(**model)
        session.add(obj)
        session.commit()
        return response_model.from_orm(obj)

    @router_metadata.put(
        f"/table/{table_type.__tablename__}/{{obj_id}}",
        summary=f"Edit a single {table_type.__name__}.",
        response_model=response_model,
        responses={
            **login_error,
            404: {"description": f"{table_type.__name__} not found"}
        }
    )
    def put(
        obj_id: int = f.Path(...),
        model: input_model = f.Body(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        obj = session.query(table_type).get(obj_id)
        if obj is None:
            raise f.HTTPException(404, f"The id '{model.id}' does not match any {table_type.__name__}.")

        obj.update(**model.__dict__)
        session.commit()

        return response_model.from_orm(obj)

    @router_metadata.patch(
        f"/table/{table_type.__tablename__}",
        summary=f"Edit multiple {table_type.__name__}s.",
        response_model=List[response_model],
        responses={
            **login_error,
        }
    )
    def patch(
        ids: List[int] = f.Query(...),
        model: dict = f.Body(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        objs = session.query(table_type).filter(table_type.id.in_(ids)).all()

        for obj in objs:
            obj.update(**{key: value for key, value in model.items() if not (key == "id" or key.startswith("_"))})
        session.commit()

        return [response_model.from_orm(obj) for obj in objs]

    @router_metadata.delete(
        f"/table/{table_type.__tablename__}/{{obj_id}}",
        summary=f"Delete a {table_type.__name__}.",
        status_code=204,
        responses={
            **login_error,
            404: {"description": f"{table_type.__name__} not found"}
        }
    )
    def delete(
        obj_id: int = f.Path(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        obj = session.query(table_type).get(obj_id)
        if obj is None:
            raise f.HTTPException(404, f"The id '{obj_id}' does not match any {table_type.__name__}.")

        session.delete(obj)
        session.commit()

    return post, put, patch, delete


editable(AlbumRole, MAlbumRoleWithoutId, MAlbumRole)
editable(Album, MAlbumWithoutId, MAlbum)
editable(Genre, MGenreWithoutId, MGenre)
editable(Layer, MLayerWithoutId, MLayer)
editable(Person, MPersonWithoutId, MPerson)
editable(SongRole, MSongRoleWithoutId, MSongRole)
editable(Song, MSongWithoutId, MSong)


__all__ = (
    "router_metadata",
)
