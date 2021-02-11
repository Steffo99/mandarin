from __future__ import annotations

import io

import celery.exceptions
import fastapi as f
import starlette.responses

from .. import dependencies
from .. import models
from .. import responses
from ...database import tables
from ...taskbus import tasks

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
    Upload a new track to the database, and start a task to process the uploaded track.
    """
    # file.file can't be directly pickled, transfer it to a bytesio object
    stream = io.BytesIO()
    while data := file.file.read(8192):
        stream.write(data)

    task = tasks.process_music.delay(
        stream=stream,
        original_filename=file.filename,
        uploader_id=ls.user.id,
        generate_entries=generate_entries
    )

    try:
        _, layer_id = task.get(timeout=15)
    except celery.exceptions.TimeoutError:
        raise f.HTTPException(202, "Task queued, but didn't finish in less than 15 seconds")

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
