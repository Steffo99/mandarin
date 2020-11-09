from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import *
from ..models import *
from ..dependencies import *

router_songs = f.APIRouter()


@router_songs.get(
    "/",
    summary="Get all songs.",
    responses={
        **login_error,
    },
    response_model=List[MSongBatch]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    return ls.session.query(Song).order_by(Song.id).limit(limit).offset(offset).all()


@router_songs.post(
    "/",
    summary="Create a new song.",
    response_model=MSongFull,
    status_code=201,
    responses={
        **login_error,
        404: {"description": "Album not found"},
    }
)
def create(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_id: Optional[int] = f.Query(None, description="The album to attach the new song to.\nCan be null for no "
                                                        "album."),
    data: MSongWithoutId = f.Body(..., description="The data for the new song."),
):
    album = ls.session.query(Album).get(album_id)
    if album is None:
        raise f.HTTPException(404, f"The id '{album_id}' does not match any album.")

    song = Song(album=album, **data)
    ls.session.add(song)
    ls.session.commit()
    ls.user.log("song.create", obj=song.id)
    ls.session.commit()

    return song


@router_songs.get(
    "/count",
    summary="Get the number of songs currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
    return session.query(Song).count()


@router_songs.get(
    "/{song_id}",
    summary="Get a single song.",
    responses={
        **login_error,
        404: {"description": "Song not found"},
    },
    response_model=MSongFull
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    song_id: int = f.Path(..., description="The id of the song to be retrieved.")
):
    layer = ls.session.query(Song).get(song_id)
    if layer is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")
    return layer


@router_songs.put(
    "/{song_id}",
    summary="Edit a song.",
    response_model=MLayerFull,
    responses={
        **login_error,
        404: {"description": "Song not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    song_id: int = f.Path(..., description="The id of the song to be edited."),
    data: MSongWithoutId = f.Body(..., description="The new data the song should have."),
):
    song: Song = ls.session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

    song.update(**data.__dict__)
    ls.user.log("song.edit.single", obj=song.id)
    ls.session.commit()
    return song


@router_songs.delete(
    "/{song_id}",
    summary="Delete a song.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Song not found"},
    }
)
def delete(
    ls: LoginSession = f.Depends(dependency_login_session),
    song_id: int = f.Path(..., description="The id of the song to be deleted.")
):
    """
    Calling this method WON'T delete the corresponding file!
    """
    song = ls.session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any layer.")
    ls.session.delete(song)
    ls.user.log("song.delete", obj=song.id)
    ls.session.commit()


__all__ = (
    "router_songs",
)
