from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import *
from .. import models
from ..dependencies import *

router_albums = f.APIRouter()


@router_albums.get(
    "/",
    summary="Get all albums.",
    responses={
        **login_error,
    },
    response_model=List[models.Album]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    """
    Get an array of all the albums currently in the database, in pages of `limit` elements and starting at the
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ls.session.query(Album).order_by(Album.id).limit(limit).offset(offset).all()


@router_albums.post(
    "/",
    summary="Create a new album.",
    responses={
        **login_error,
    },
    response_model=models.AlbumOutput,
)
def create(
    ls: LoginSession = f.Depends(dependency_login_session),
    data: models.AlbumInput = f.Body(..., description="The data the new album should have."),
):
    """
    Create a new, **empty** album with the data specified in the body of the request.
    """
    album = Album(**data.__dict__)
    ls.session.add(data)
    ls.session.commit()
    ls.user.log("album.create", obj=album.id)
    ls.session.commit()
    return album


@router_albums.get(
    "/count",
    summary="Get the total number of albums.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
    """
    Get the total number of albums.

    Since it doesn't require any login, it can be useful to display some information on an "instance preview" page.
    """
    return session.query(Album).count()


@router_albums.patch(
    "/involve",
    summary="Involve a person with some albums.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Role / person not found"},
    }
)
def edit_multiple_involve(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_ids: List[int] = f.Query(..., description="The ids of the albums to involve the person with."),
    person_id: int = f.Query(..., description="The ids of the person to involve."),
    role_id: int = f.Query(..., description="The id of the role of the involvement."),
):
    """
    Connect the specified person to the specified albums detailing a role as the role of their involvement.

    For example, "[Luis Fonsi](https://en.wikipedia.org/wiki/Luis_Fonsi)" should be involved with the album
    "[Vida](https://en.wikipedia.org/wiki/Vida_(Luis_Fonsi_album))" with the role "Artist".

    Non-existing `album_ids` passed to the method will be silently skipped, while a 404 error will be raised for
    non-existing people or roles.

    Trying to create an involvement that already exists will result in that involvement being skipped.
    """
    role = ls.get(Role, role_id)
    person = ls.get(Person, person_id)
    for album in ls.group(Album, album_ids):
        AlbumInvolvement.make(session=ls.session, role=role, album=album, person=person)
        ls.user.log("album.edit.multiple.involve", obj=album.id)
    ls.session.commit()
    return f.Response(status_code=204)


@router_albums.patch(
    "/uninvolve",
    summary="Uninvolve a person from some albums.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Role / person not found"},
    }
)
def edit_multiple_uninvolve(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_ids: List[int] = f.Query(..., description="The ids of the albums to uninvolve the person from."),
    person_id: int = f.Query(..., description="The ids of the person to uninvolve."),
    role_id: int = f.Query(..., description="The id of the role of the involvement."),
):
    """
    The opposite of _involve_: delete the connection between the specified person and the specified albums that has
    the specified role.

    Non-existing `album_ids` passed to the method will be silently skipped, while a 404 error will be raised for
    non-existing people or roles.

    Involvements that don't exist will be silently ignored.
    """
    role = ls.get(Role, role_id)
    person = ls.get(Person, person_id)
    for song in ls.group(Album, album_ids):
        AlbumInvolvement.unmake(session=ls.session, role=role, song=song, person=person)
        ls.user.log("album.edit.multiple.uninvolve", obj=song.id)
    ls.session.commit()
    return f.Response(status_code=204)


@router_albums.patch(
    "/classify",
    summary="Add a genre to some albums.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_multiple_classify(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_ids: List[int] = f.Query(..., description="The ids of the albums to add a genre to."),
    genre_id: int = f.Query(..., description="The id of the genre to add."),
):
    """
    Add the specified genre to all the specified albums.

    Non-existing `album_ids` passed to the method will be silently skipped, while a 404 error will be raised for a
    non-existing genre.
    """
    genre = ls.get(Genre, genre_id)
    for album in ls.group(Album, album_ids):
        album.genres.append(genre)
        ls.user.log("album.edit.multiple.classify", obj=album.id)
    ls.session.commit()
    return f.Response(status_code=204)


@router_albums.patch(
    "/declassify",
    summary="Remove a genre from some albums.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_multiple_declassify(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_ids: List[int] = f.Query(..., description="The ids of the albums to remove a genre from."),
    genre_id: int = f.Query(..., description="The id of the genre to remove."),
):
    """
    Remove the specified genre from all the specified albums.

    Non-existing `album_ids` passed to the method will be silently skipped, while a 404 error will be raised for a
    non-existing genre.
    """
    genre = ls.get(Genre, genre_id)
    for album in ls.group(Album, album_ids):
        album.genres.remove(genre)
        ls.user.log("album.edit.multiple.declassify", obj=album.id)
    ls.session.commit()
    return f.Response(status_code=204)


@router_albums.patch(
    "/merge",
    summary="Merge two or more albums.",
    status_code=204,
    responses={
        **login_error,
        400: {"description": "Not enough albums specified"}
    },
)
def merge(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_ids: List[int] = f.Query(..., description="The ids of the albums to merge."),
):
    """
    Move the songs of all the specified albums into a single one, which will have the metadata of the first album
    specified.
    """

    if len(album_ids) < 2:
        raise f.HTTPException(400, "Not enough albums specified")

    # Create a new session in SERIALIZABLE isolation mode, so nothing can be added to the genres to be merged.
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Get the first album
    main_album = rr_session.query(Album).get(album_ids[0])
    ls.user.log("album.merge.to", obj=main_album.id)

    # Get the other albums
    other_albums = rr_session.query(Album).filter(Album.id.in_(album_ids[1:])).all()

    # Replace and delete the other albums
    for merged_album in other_albums:
        for song in merged_album.songs:
            song.album = main_album
        ls.user.log("album.merge.from", obj=merged_album.id)
        rr_session.delete(merged_album)

    rr_session.commit()
    rr_session.close()

    ls.session.commit()
    return f.Response(status_code=204)


@router_albums.get(
    "/{album_id}",
    summary="Get a single album.",
    responses={
        **login_error,
        404: {"description": "Album not found"},
    },
    response_model=models.AlbumOutput
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_id: int = f.Path(..., description="The id of the album to be retrieved.")
):
    """
    Get full information for the album with the specified `album_id`.
    """
    return ls.get(Album, album_id)


@router_albums.put(
    "/{album_id}",
    summary="Edit an album.",
    response_model=models.AlbumOutput,
    responses={
        **login_error,
        404: {"description": "Album not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_id: int = f.Path(..., description="The id of the album to be edited."),
    data: models.AlbumInput = f.Body(..., description="The new data the album should have."),
):
    """
    Replace the data of the album with the specified `album_id` with the data passed in the request body.
    """
    album = ls.get(Album, album_id)
    album.update(**data.__dict__)
    ls.user.log("album.edit.single", obj=album.id)
    ls.session.commit()
    return album


@router_albums.delete(
    "/{album_id}",
    summary="Delete an album.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Album not found"},
    }
)
def delete(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_id: int = f.Path(..., description="The id of the album to be deleted."),
):
    """
    Delete the album having the specified `album_id`.

    Note that the contained songs will not be deleted; they will become orphaned instead.
    """
    album = ls.get(Album, album_id)
    ls.session.delete(album)
    ls.user.log("album.delete", obj=album.id)
    ls.session.commit()
    return f.Response(status_code=204)


__all__ = (
    "router_albums",
)
