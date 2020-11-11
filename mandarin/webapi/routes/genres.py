from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import *
from .. import models
from ..dependencies import *

router_genres = f.APIRouter()


@router_genres.get(
    "/",
    summary="Get all genres.",
    responses={
        **login_error,
    },
    response_model=List[models.GenreOutput]
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
        409: {"description": "Duplicate genre name"}
    },
    response_model=models.GenreOutput,
)
def create(
    ls: LoginSession = f.Depends(dependency_login_session),
    data: models.GenreInput = f.Body(..., description="The new data the genre should have."),
):
    genre = ls.session.query(Genre).filter_by(name=data.name).one_or_none()
    if genre is not None:
        raise f.HTTPException(409, f"The genre '{data.name}' already exists.")

    genre = Genre.make(session=ls.session, **data.dict())
    ls.user.log("genre.create", obj=genre.id)
    ls.session.commit()
    return genre


@router_genres.get(
    "/count",
    summary="Get the number of genres currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
    return session.query(Genre).count()


@router_genres.patch(
    "/merge",
    summary="Merge two or more genres.",
    status_code=204,
    responses={
        **login_error,
        400: {"description": "Not enough genres specified"}
    },
)
def merge(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_ids: List[int] = f.Query(..., description="The ids of the genres to merge."),
):
    """
    The first genre will be used as base and will keep its name and description.
    """

    if len(genre_ids) < 2:
        raise f.HTTPException(400, "Not enough genres specified")

    # Create a new session in SERIALIZABLE isolation mode, so nothing can be added to the genres to be merged.
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Get the first genre
    main_genre = rr_session.query(Genre).get(genre_ids[0])
    ls.user.log("genre.merge.to", obj=main_genre.id)

    # Get the other genres
    other_genres = rr_session.query(Genre).filter(Genre.id.in_(genre_ids[1:])).all()

    # Replace and delete the other genres
    for merged_genre in other_genres:
        for song in merged_genre.songs:
            song.genres.remove(merged_genre)
            song.genres.append(main_genre)
        for album in merged_genre.albums:
            album.genres.remove(merged_genre)
            album.genres.append(main_genre)
        ls.user.log("genre.merge.from", obj=merged_genre.id)
        rr_session.delete(merged_genre)

    rr_session.commit()
    rr_session.close()

    ls.session.commit()
    return f.Response(status_code=204)


@router_genres.get(
    "/{genre_id}",
    summary="Get a single genre.",
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    },
    response_model=models.GenreOutput
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be retrieved.")
):
    return ls.get(Genre, genre_id)


@router_genres.put(
    "/{genre_id}",
    summary="Edit a genre.",
    response_model=models.GenreOutput,
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be edited."),
    data: models.GenreInput = f.Body(..., description="The new data the genre should have."),
):
    genre = ls.get(Genre, genre_id)
    genre.update(**data.dict())
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
    return f.Response(status_code=204)


__all__ = (
    "router_genres",
)
