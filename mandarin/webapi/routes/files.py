from __future__ import annotations
import starlette.responses
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm.session
import celery.exceptions

from ...database import tables
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses


router_files = f.APIRouter()


@router_files.post(
    "/layer",
    summary="Upload an audio track.",
    response_model=models.LayerOutput,
    status_code=201,
    responses={
        **responses.celery_timeout,
        **responses.login_error,
    }
)
def upload_layer(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    file: f.UploadFile = f.File(..., description="The file to be uploaded."),
    generate_entries: bool = f.Query(True, description="Automatically generate entries (song, album, people) for the "
                                                       "uploaded file.")
):
    """
    Upload a new track to the database.

    If `generate_entries` is set, `layer_data['song_id']` will be ignored.
    """

    task = tasks.process_music.delay(
        stream=file.file,
        original_filename=file.filename,
        uploader_id=ls.user.id,
        generate_entries=generate_entries
    )

    try:
        _, layer_id = task.get(timeout=5)
    except celery.exceptions.TimeoutError:
        raise f.HTTPException(202, "Task queued, but didn't finish in less than 5 seconds")

    layer = ls.session.query(tables.Layer).get(layer_id)
    return layer


@router_files.get(
    "/{file_id}",
    summary="Download a file.",
    response_class=starlette.responses.FileResponse,
    responses={
        **responses.login_error,
        404: {"description": "File not found"},
    }
)
async def download_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    file_id: int = f.Path(..., description="The id of the file to be downloaded.")
):
    """
    Download a single raw file from the database, without any tags applied.
    """
    file = ls.get(tables.File, file_id)
    return starlette.responses.FileResponse(file.name, media_type=file.mime_type)


__all__ = (
    "router_files",
)
