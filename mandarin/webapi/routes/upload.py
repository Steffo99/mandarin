from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm.session

from ...database import *
from ..models.parse import *
from ..utils.auth import *
from ..utils.upload import *


router_upload = f.APIRouter()


@router_upload.post(
    "/track/auto",
    summary="Upload a track, and infer its metadata automatically.",
    response_model=UploadResult,
    status_code=201,
    responses={
        401: {"description": "Not logged in"},
    }
)
def track_auto(
    file: f.UploadFile = f.File(...),
    user: User = f.Depends(find_or_create_user),
) -> UploadResult:
    """
    Upload a new audio track.

    If the metadata matches a song that already exists, add it as a new layer for that song.

    If the metadata does not match any existant song, create a new song (and eventually album), and add the first
    layer to it.
    """

    # Parse and save the file
    parse, filename = save_uploadfile(file)

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Add the file to the session
    file_db = File.make(session=session, name=filename, uploader=user)

    # Use the first parse to create the metadata
    song = auto_song(session=session, parse=parse)

    # Create the layer
    layer = SongLayer(song=song, file=file_db)
    session.add(layer)

    # Commit the changes in the session
    session.commit()

    # Create the return value
    result = UploadResult(layer=UploadLayer.from_orm(layer))

    # Close the session
    session.close()

    return result


@router_upload.post(
    "/track/add",
    summary="Upload a track, and add it as a new layer of a song.",
    response_model=UploadResult,
    status_code=201,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Song not found"},
    }
)
def track_add(
    song_id: int,
    file: f.UploadFile = f.File(...),
    user: User = f.Depends(find_or_create_user)
) -> UploadResult:
    """
    Upload a new audio track.

    A new layer will be created for the song having the specified id.

    The metadata of the track will be discarded.
    """

    # Parse and save the file
    parse, filename = save_uploadfile(file)

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Add the file to the session
    file_db = File.make(session=session, name=filename, uploader=user)

    # Find the song
    song: Optional[Song] = session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

    # Create the layer
    layer = SongLayer(song=song, file=file_db)
    session.add(layer)

    # Commit the changes in the session
    session.commit()

    # Create the return value
    result = UploadResult(layer=UploadLayer.from_orm(layer))

    # Close the session
    session.close()

    return result


__all__ = (
    "router_upload",
)
