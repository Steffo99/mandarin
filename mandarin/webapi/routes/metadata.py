from royalnet.typing import *
import sqlalchemy.orm
import fastapi as f

from ...database import *
from ..utils.auth import *
from ..models.parse import *


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


__all__ = (
    "router_metadata",
)
