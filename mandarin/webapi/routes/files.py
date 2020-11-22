from __future__ import annotations
import starlette.responses
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm.session
import datetime

from ...database import *
from .. import models
from ..dependencies import *
from ..utils.upload import *


router_files = f.APIRouter()


@router_files.post(
    "/layer",
    summary="Upload an audio track.",
    response_model=models.LayerOutput,
    status_code=201,
    responses={
        **login_error,
    }
)
def upload_layer(
    ls: LoginSession = f.Depends(dependency_login_session),
    file: f.UploadFile = f.File(..., description="The file to be uploaded."),
    name: str = f.Query("Default", description="The name of the created layer."),
    description: Optional[str] = f.Query(None, description="The description of the created layer."),
):
    """
    Upload a new track to the database.

    The metadata of the file will be stripped and discarded.

    A new unattached Layer object will be created and returned.
    """

    # Parse and save the file
    parse, filename = save_uploadfile(file)

    # Add the file to the session
    file_db = File.make(session=ls.session, name=filename, _uploader=ls.user.sub)
    layer = Layer(name=name, description=description, file=file_db)
    ls.session.add(layer)

    # Log the upload
    ls.user.log("files.upload.layer", obj=file_db.id)

    # Commit the session
    ls.session.commit()

    # Return the result
    return layer


@router_files.post(
    "/layer/auto",
    summary="Upload an audio track, and autogenerate its entities.",
    response_model=models.LayerOutput,
    status_code=201,
    responses={
        **login_error,
    }
)
def upload_layer_auto(
    ls: LoginSession = f.Depends(dependency_login_session),
    file: f.UploadFile = f.File(..., description="The file to be uploaded."),
    name: str = f.Query("Default", description="The name of the created layer."),
    description: Optional[str] = f.Query(None, description="The description of the created layer."),
):
    """
    Upload a new audio track.

    The metadata of the file will be parsed using mutagen, and will be used to create the database entities for the
    track.

    If the metadata matches a song that already exists, the file will be added as a new layer for that song.

    If the metadata does not match any existing song, a new song (and possibily a new album) will be created,
    and the file will be added to it as the first layer.
    """

    # Parse and save the file
    parse, filename = save_uploadfile(file)

    # Create a new session in SERIALIZABLE isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    # Do not use the dependency for more control
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Add the file to the session
    file_db = File.make(session=rr_session, name=filename, _uploader=ls.user.id)

    # Use the first parse to create the metadata
    song = auto_song(session=rr_session, parse=parse)

    # Create the layer
    layer = Layer(song=song, file=file_db, name=name, description=description)
    rr_session.add(layer)

    # Log the upload
    ls.user.log("files.upload.layer.auto", obj=file_db.id)

    # Commit the changes in the session
    rr_session.commit()
    ls.session.commit()

    # Prepare the return value
    result = models.LayerOutput.from_orm(layer)

    # Close the session
    rr_session.close()

    return result


@router_files.get(
    "/{file_id}",
    summary="Download a file.",
    response_class=starlette.responses.FileResponse,
    responses={
        **login_error,
        404: {"description": "File not found"},
    }
)
async def download_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    file_id: int = f.Path(..., description="The id of the file to be downloaded.")
):
    """
    Download a single raw file from the database, without any tags applied.
    """
    file = ls.get(File, file_id)
    return starlette.responses.FileResponse(file.name, media_type=file.mime_type)


__all__ = (
    "router_files",
)
