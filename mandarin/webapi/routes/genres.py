from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import tables, Session
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses

router_genres = f.APIRouter()


@router_genres.get(
    "/",
    summary="Get all genres.",
    responses={
        **responses.login_error,
    },
    response_model=List[models.GenreOutput]
)
def get_all(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    """
    Get an array of all the genres currently in the database, in pages of `limit` elements and starting at the
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ls.session.query(tables.Genre).order_by(tables.Genre.id).limit(limit).offset(offset).all()


@router_genres.post(
    "/",
    summary="Create a new genre.",
    responses={
        **responses.login_error,
        409: {"description": "Duplicate genre name"}
    },
    response_model=models.GenreOutput,
)
def create(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    data: models.GenreInput = f.Body(..., description="The new data the genre should have."),
):
    """
    Create a new genre with the data specified in the body of the request.
    """
    genre = ls.session.query(tables.Genre).filter_by(name=data.name).one_or_none()
    if genre is not None:
        raise f.HTTPException(409, f"The genre '{data.name}' already exists.")

    genre = tables.Genre.make(session=ls.session, **data.dict())
    ls.user.log("genre.create", obj=genre.id)
    ls.session.commit()
    return genre


@router_genres.get(
    "/count",
    summary="Get the total number of genres.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependencies.dependency_db_session)
):
    """
    Get the total number of genres.

    Since it doesn't require any login, it can be useful to display some information on an "instance preview" page.
    """
    return session.query(tables.Genre).count()


@router_genres.patch(
    "/merge",
    summary="Merge two or more genres.",
    status_code=204,
    responses={
        **responses.login_error,
        400: {"description": "Not enough genres specified"}
    },
)
def merge(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    genre_ids: List[int] = f.Query(..., description="The ids of the genres to merge."),
):
    """
    Merge the songs and albums of the specified genre into a single one, which will have the metadata of the first
    genre specified.
    """

    if len(genre_ids) < 2:
        raise f.HTTPException(400, "Not enough genres specified")

    # Create a new session in SERIALIZABLE isolation mode, so nothing can be added to the genres to be merged.
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Get the first genre
    main_genre = rr_session.query(tables.Genre).get(genre_ids[0])
    ls.user.log("genre.merge.to", obj=main_genre.id)

    # Get the other genres
    other_genres = rr_session.query(tables.Genre).filter(tables.Genre.id.in_(genre_ids[1:])).all()

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
        **responses.login_error,
        404: {"description": "Genre not found"},
    },
    response_model=models.GenreOutput
)
def get_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be retrieved.")
):
    """
    Get full information for the genre with the specified `genre_id`.
    """
    return ls.get(tables.Genre, genre_id)


@router_genres.put(
    "/{genre_id}",
    summary="Edit a genre.",
    response_model=models.GenreOutput,
    responses={
        **responses.login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be edited."),
    data: models.GenreInput = f.Body(..., description="The new data the genre should have."),
):
    """
    Replace the data of the genre with the specified `genre_id` with the data passed in the request body.
    """
    genre = ls.get(tables.Genre, genre_id)
    genre.update(**data.dict())
    ls.user.log("genre.edit.single", obj=genre.id)
    ls.session.commit()
    return genre


@router_genres.delete(
    "/{genre_id}",
    summary="Delete a genre.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Genre not found"},
    }
)
def delete(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    genre_id: int = f.Path(..., description="The id of the genre to be deleted."),
):
    """
    Delete the genre having the specified `genre_id`, also disconnecting all songs from it.
    """
    genre = ls.get(tables.Genre, genre_id)
    ls.session.delete(genre)
    ls.user.log("genre.delete", obj=genre.id)
    ls.session.commit()
    return f.Response(status_code=204)


__all__ = (
    "router_genres",
)
