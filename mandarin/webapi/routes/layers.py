from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import pydantic as p
import sqlalchemy.orm
import datetime

from ...database import *
from .. import models
from ..dependencies import *
from ..utils.upload import *

router_layers = f.APIRouter()


@router_layers.get(
    "/",
    summary="Get all layers.",
    responses={
        **login_error,
    },
    response_model=List[models.LayerOutput]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    """
    Get an array of all the layers currently in the database, in pages of `limit` elements and starting at the
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ls.session.query(Layer).order_by(Layer.id).limit(limit).offset(offset).all()


@router_layers.get(
    "/count",
    summary="Get the number of layers currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
    """
    Get the total number of layers.

    Since it doesn't require any login, it can be useful to display some information on an "instance preview" page.
    """
    return session.query(Layer).count()


@router_layers.patch(
    "/move",
    summary="Move some layers to a different song.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Song not found"},
    },
)
def edit_multiple_move(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_ids: List[int] = f.Query(..., description="The ids of the layers that should be moved."),
    song_id: int = f.Query(...,  description="The id of the song the layers should be moved to."),
):
    song = ls.get(Song, song_id)
    for layer in ls.group(Layer, layer_ids):
        layer.song = song
        ls.user.log("layer.edit.multiple.move", obj=layer.id)
    ls.session.commit()


@router_layers.patch(
    "/rename",
    summary="Rename some layers.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Song not found"},
    },
)
def edit_multiple_rename(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_ids: List[int] = f.Query(..., description="The ids of the layers that should be renamed."),
    name: str = f.Query(...,  description="The name the layers should be renamed to."),
):
    """
    Non-existing layer_ids will be ignored.
    """
    for layer in ls.group(Layer, layer_ids):
        layer.name = name
        ls.user.log("layer.edit.multiple.rename", obj=layer.id)

    ls.session.commit()


@router_layers.get(
    "/{layer_id}",
    summary="Get a single layer.",
    responses={
        **login_error,
        404: {"description": "Layer not found"},
    },
    response_model=models.LayerOutput
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_id: int = f.Path(..., description="The id of the layer to be retrieved.")
):
    return ls.get(Layer, layer_id)


@router_layers.put(
    "/{layer_id}",
    summary="Edit a layer.",
    response_model=models.LayerOutput,
    responses={
        **login_error,
        404: {"description": "Layer not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_id: int = f.Path(..., description="The id of the layer to be edited."),
    data: models.LayerInput = f.Body(..., description="The new data the layer should have."),
):
    layer = ls.get(Layer, layer_id)
    layer.update(**data.__dict__)
    ls.user.log("layer.edit.single", obj=layer.id)
    ls.session.commit()
    return layer


@router_layers.delete(
    "/{layer_id}",
    summary="Delete a layer.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Layer not found"},
    }
)
def delete(
    ls: LoginSession = f.Depends(dependency_login_session),
    layer_id: int = f.Path(..., description="The id of the layer to be deleted.")
):
    """
    Calling this method WON'T delete the corresponding file!
    """
    layer = ls.get(Layer, layer_id)
    ls.session.delete(layer)
    ls.user.log("layer.delete", obj=layer.id)
    ls.session.commit()
    return f.Response(status_code=204)


__all__ = (
    "router_layers",
)
