from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm.session
import datetime

from ...database import *
from ..models.database import *
from ..dependencies import *
from ..utils.upload import *


router_upload = f.APIRouter()


@router_upload.post(
    "/track/auto",
    summary="Upload a track, and infer its metadata automatically.",
    response_model=MLayerFull,
    status_code=201,
    responses={
        401: {"description": "Not logged in"},
    }
)
def track_auto(
    ls: LoginSession = f.Depends(dependency_login_session),
    file: f.UploadFile = f.File(...),
) -> MLayerFull:
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
    # Do not use the dependency for more control
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Add the file to the session
    file_db = File.make(session=rr_session, name=filename, _uploader=ls.user.sub)

    # Use the first parse to create the metadata
    song = auto_song(session=rr_session, parse=parse)

    # Create the layer
    layer = Layer(song=song, file=file_db)
    rr_session.add(layer)

    # Log the upload
    ls.user.log("upload.auto", obj=layer.id)

    # Commit the changes in the session
    rr_session.commit()

    # Create the return value
    result = MLayerFull.from_orm(layer)

    # Close the session
    rr_session.close()

    ls.session.commit()

    return result





__all__ = (
    "router_upload",
)
