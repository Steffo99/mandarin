from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import pydantic as p
import sqlalchemy.orm

from ...database import *
from ..models import *
from ..dependencies import *
from ..utils.upload import *

router_layers = f.APIRouter()


@router_layers.get(
    "/",
    summary="Get all layers.",
    responses={
        **login_error,
    },
    response_model=List[MLayer]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    layers = ls.session.query(Layer).order_by(Layer.id).limit(limit).offset(offset).all()
    return layers
    # return [MLayer.from_orm(obj) for obj in objs]


@router_layers.get(
    "/{layer_id}",
    summary="Get a single layer.",
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Layer not found"},
    },
    response_model=MLayerFull
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_id: int = f.Path(..., description="The id of the layer to be retrieved.")
):
    layer = ls.session.query(Layer).get(layer_id)
    if layer is None:
        raise f.HTTPException(404, f"The id '{layer_id}' does not match any layer.")
    return layer


@router_layers.post(
    "/",
    summary="Create a new layer from a audio file.",
    response_model=MLayerFull,
    status_code=201,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Song not found"},
    }
)
def create_upload(
    ls: LoginSession = f.Depends(dependency_login_session),
    song_id: int = f.Query(..., description="The song to attach the new layer to."),
    file: f.UploadFile = f.File(..., description="The file to be uploaded."),
):
    """
    Add a new layer to a song by uploading a new audio file.

    The metadata of the file will be discarded.
    """

    # Parse and save the file
    parse, filename = save_uploadfile(file)

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    # Do not use the dependency for more control
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Add the file to the session
    file_db = File.make(session=rr_session, name=filename, uploader=ls.user)

    # Find the song
    song: Optional[Song] = rr_session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

    # Create the layer
    layer = Layer(song=song, file=file_db)
    rr_session.add(layer)

    # Log the upload
    ls.user.log(session=rr_session, action="layer.create.upload", obj=layer.id)

    # Commit the changes in the session
    rr_session.commit()

    # Create the return value
    result = MLayerFull.from_orm(layer)

    # Close the session
    rr_session.close()

    return result


@router_layers.put(
    "/{layer_id}",
    summary="Edit a layer.",
    status_code=204,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Layer not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_id: int = f.Path(..., description="The id of the layer to be edited."),
    data: MLayerWithoutId = f.Body(..., description="The new data the layer should have."),
):
    layer: Layer = ls.session.query(Layer).get(layer_id)
    if layer is None:
        raise f.HTTPException(404, f"The id '{layer_id}' does not match any layer.")

    layer.update(**data)
    ls.user.log("layer.edit.single", obj=layer.id)
    ls.session.commit()


@router_layers.patch(
    "/",
    summary="Move some layers to a different song.",
    responses={
        **login_error,
        404: {"description": "Song not found"},
    },
    status_code=204,
)
def edit_multiple(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_ids: List[int] = f.Query(..., description="The ids of the layers that should be moved."),
    song_id: int = f.Query(...,  description="The id of the song the layers should be moved to."),
):
    """
    Non-existing layer_ids will be ignored.
    """
    song: Optional[Song] = ls.session.query(Song).get(song_id)
    if song is None:
        raise f.HTTPException(404, f"The id '{song_id}' does not match any song.")

    layers = ls.session.query(Layer).filter(Layer.id.in_(layer_ids)).all()
    for layer in layers:
        layer.song = song
        ls.user.log("layer.edit.multiple", obj=layer.id)

    ls.session.commit()


@router_layers.delete(
    "/{layer_id}",
    summary="Delete a layer.",
    status_code=204,
    responses={
        401: {"description": "Not logged in"},
        404: {"description": "Layer not found"},
    }
)
def delete(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_id: int = f.Path(..., description="The id of the layer to be deleted.")
):
    layer = ls.session.query(Layer).get(layer_id)
    if layer is None:
        raise f.HTTPException(404, f"The id '{layer_id}' does not match any layer.")
    ls.session.delete(layer)
    ls.user.log("layer.delete", obj=layer.id)
    ls.session.commit()


__all__ = (
    "router_layers",
)
