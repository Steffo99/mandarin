from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import *
from ..models import *
from ..dependencies import *

router_genres = f.APIRouter()


@router_genres.get(
    "/",
    summary="Get all genres.",
    responses={
        **login_error,
    },
    response_model=List[MGenre]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    return ls.session.query(Genre).order_by(Genre.id).limit(limit).offset(offset).all()


@router_genres.post(
    "/",
    summary="Create a new genre.",
    responses={
        **login_error,
        409: {"description": "A genre with that name already exists."}
    },
    response_model=MGenreFull,
)
def create(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_name: str = f.Query(..., description="The name of the genre to retrieve or create."),
):
    genre = ls.session.query(Genre).filter_by(name=genre_name).one_or_none()
    if genre is not None:
        raise f.HTTPException(409, f"The genre '{genre_name}' already exists.")

    genre = Genre.make(session=ls.session, name=genre_name)
    ls.user.log("genre.create.post", obj=genre.id)
    ls.session.commit()
    return genre


@router_genres.put(
    "/by-name/{genre_name}",
    summary="Get or create a new genre.",
    responses={
        **login_error,
    },
    response_model=MGenreFull,
)
def create_byname(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_name: str = f.Path(..., description="The name of the genre to retrieve or create."),
):
    genre = Genre.make(session=ls.session, name=genre_name)
    ls.user.log("genre.create.put", obj=genre.id)
    ls.session.commit()
    return genre


@router_genres.get(
    "/count",
    summary="Get the number of layers currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
    return session.query(Genre).count()


@router_genres.get(
    "/{genre_id}",
    summary="Get a single genre.",
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    },
    response_model=MGenreFull
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be retrieved.")
):
    return ls.get(Genre, genre_id)


@router_genres.put(
    "/{genre_id}",
    summary="Edit a genre.",
    response_model=MGenreFull,
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be edited."),
    data: MGenreWithoutId = f.Body(..., description="The new data the genre should have."),
):
    genre = ls.get(Genre, genre_id)
    genre.update(**data.__dict__)
    ls.user.log("genre.edit.single", obj=genre.id)
    ls.session.commit()
    return genre


@router_genres.delete(
    "/{genre_id}",
    summary="Delete a genre.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    }
)
def delete(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be deleted."),
):
    """
    Calling this method WON'T delete the corresponding file!
    """
    genre = ls.get(Genre, genre_id)
    ls.session.delete(genre)
    ls.user.log("genre.delete", obj=genre.id)
    ls.session.commit()


__all__ = (
    "router_genres",
)
