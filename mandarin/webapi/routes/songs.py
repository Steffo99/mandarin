from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import tables, Session
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses

router_songs = f.APIRouter()


@router_songs.get(
    "/",
    summary="Get all songs.",
    responses={
        **responses.login_error,
    },
    response_model=List[models.Song]
)
def get_all(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    """
    Get an array of all the songs currently in the database, in pages of `limit` elements and starting at the
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ls.session.query(tables.Song).order_by(tables.Song.id).limit(limit).offset(offset).all()


@router_songs.post(
    "/",
    summary="Create a new song.",
    response_model=models.SongOutput,
    status_code=201,
    responses={
        **responses.login_error,
        404: {"description": "Album not found"},
    }
)
def create(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    album_id: Optional[int] = f.Query(None,
                                      description="The album to attach the new song to.\nCan be null for no album."),
    data: models.SongInput = f.Body(..., description="The data for the new song."),
):
    """
    Create a new song with no layers and the data specified in the body of the request.
    """
    album = ls.get(tables.Album, album_id)
    song = tables.Song(album=album, **data.__dict__)
    ls.session.add(song)
    ls.session.commit()
    ls.user.log("song.create", obj=song.id)
    ls.session.commit()
    return song


@router_songs.get(
    "/count",
    summary="Get the number of songs currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependencies.dependency_db_session)
):
    """
    Get the total number of songs.

    Since it doesn't require any login, it can be useful to display some information on an "instance preview" page.
    """
    return session.query(tables.Song).count()


@router_songs.patch(
    "/move",
    summary="Move some songs to a different album.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Album not found"}
    }
)
def edit_multiple_move(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs that should be moved."),
    album_id: Optional[int] = f.Query(..., description="The id of the album the layers should be moved to."),
):
    """
    Change the album the specified songs are associated with.
    """
    if album_id:
        album = ls.get(tables.Album, album_id)
    else:
        album = None

    for song in ls.group(tables.Song, song_ids):
        song.album = album
        ls.user.log("song.edit.multiple.move", obj=song.id)

    ls.session.commit()
    return f.Response(status_code=204)


@router_songs.patch(
    "/involve",
    summary="Involve a person with some songs.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Role / person not found"},
    }
)
def edit_multiple_involve(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs to involve the person with."),
    person_id: int = f.Query(..., description="The ids of the person to involve."),
    role_id: int = f.Query(..., description="The id of the role of the involvement."),
):
    """
    Connect the specified person to the specified songs detailing a role as the role of their involvement.

    For example, "[Luis Fonsi](https://en.wikipedia.org/wiki/Luis_Fonsi)" should be involved with the song
    "[Despacito](https://en.wikipedia.org/wiki/Despacito)" with the role "Artist".

    Non-existing `song_ids` passed to the method will be silently skipped, while a 404 error will be raised for
    non-existing people or roles.

    Trying to create an involvement that already exists will result in that involvement being skipped.
    """
    role = ls.get(tables.Role, role_id)
    person = ls.get(tables.Person, person_id)
    for song in ls.group(tables.Song, song_ids):
        tables.SongInvolvement.make(session=ls.session, role=role, song=song, person=person)
        ls.user.log("song.edit.multiple.involve", obj=song.id)
    ls.session.commit()
    return f.Response(status_code=204)


@router_songs.patch(
    "/uninvolve",
    summary="Uninvolve a person from some songs.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Role / person not found"},
    }
)
def edit_multiple_uninvolve(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs to uninvolve the person from."),
    person_id: int = f.Query(..., description="The ids of the person to uninvolve."),
    role_id: int = f.Query(..., description="The id of the role of the involvement."),
):
    """
    The opposite of _involve_: delete the connection between the specified person and the specified songs that has
    the specified role.

    Non-existing `song_ids` passed to the method will be silently skipped, while a 404 error will be raised for
    non-existing people or roles.

    Involvements that don't exist will be silently ignored.
    """
    role = ls.get(tables.Role, role_id)
    person = ls.get(tables.Person, person_id)
    for song in ls.group(tables.Song, song_ids):
        tables.SongInvolvement.unmake(session=ls.session, role=role, song=song, person=person)
        ls.user.log("song.edit.multiple.uninvolve", obj=song.id)
    ls.session.commit()


@router_songs.patch(
    "/classify",
    summary="Add a genre to some songs.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_multiple_classify(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs to add a genre to."),
    genre_id: int = f.Query(..., description="The id of the genre to add."),
):
    """
    Add the specified genre to all the specified songs.

    Non-existing `song_ids` passed to the method will be silently skipped, while a 404 error will be raised for a
    non-existing genre.
    """
    genre = ls.get(tables.Genre, genre_id)
    for song in ls.group(tables.Song, song_ids):
        song.genres.append(genre)
        ls.user.log("song.edit.multiple.classify", obj=song.id)
    ls.session.commit()


@router_songs.patch(
    "/declassify",
    summary="Remove a genre from some songs.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Genre not found"},
    }
)
def edit_multiple_declassify(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs to remove a genre from."),
    genre_id: int = f.Query(..., description="The id of the genre to remove."),
):
    """
    Remove the specified genre from all the specified songs.

    Non-existing `song_ids` passed to the method will be silently skipped, while a 404 error will be raised for a
    non-existing genre.
    """
    genre = ls.get(tables.Genre, genre_id)
    for song in ls.group(tables.Song, song_ids):
        song.genres.remove(genre)
        ls.user.log("song.edit.multiple.declassify", obj=song.id)
    ls.session.commit()


@router_songs.patch(
    "/group",
    summary="Set the disc number of some songs.",
    status_code=204,
    responses={
        **responses.login_error,
    }
)
def edit_multiple_group(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs to group."),
    disc_number: Optional[int] = f.Query(None, description="The number of the disc to group the songs in, "
                                                           "or None to clear the disc number.", ge=1),
):
    """
    Change the disc number of all the specified songs.
    """
    for song in ls.group(tables.Song, song_ids):
        song.disc = disc_number
        ls.user.log("song.edit.multiple.group", obj=song.id)
    ls.session.commit()


@router_songs.patch(
    "/calendarize",
    summary="Set the year of some songs.",
    status_code=204,
    responses={
        **responses.login_error,
    }
)
def edit_multiple_calendarize(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the songs to calendarize."),
    year: Optional[int] = f.Query(None, description="The year to set the songs to, or None to clear the year."),
):
    """
    Change the release year of all the specified songs.
    """
    for song in ls.group(tables.Song, song_ids):
        song.year = year
        ls.user.log("song.edit.multiple.calendarize", obj=song.id)
    ls.session.commit()


@router_songs.patch(
    "/merge",
    summary="Merge the layers of two or more songs.",
    status_code=204,
    responses={
        **responses.login_error,
        400: {"description": "Not enough genres specified"}
    },
)
def merge(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_ids: List[int] = f.Query(..., description="The ids of the genres to merge."),
):
    """
    Move the layers of all the specified songs into a single one, which will have the metadata of the first song
    specified.
    """

    if len(song_ids) < 2:
        raise f.HTTPException(400, "Not enough songs specified")

    # Create a new session in SERIALIZABLE isolation mode, so nothing can be added to the genres to be merged.
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Get the first genre
    main_song = rr_session.query(tables.Song).get(song_ids[0])
    ls.user.log("song.merge.to", obj=main_song.id)

    # Get the other genres
    other_songs = rr_session.query(tables.Song).filter(tables.Song.id.in_(song_ids[1:])).all()

    # Replace and delete the other genres
    for merged_song in other_songs:
        for layer in merged_song.layers:
            layer.song = main_song

        ls.user.log("song.merge.from", obj=merged_song.id)
        rr_session.delete(merged_song)

    rr_session.commit()
    rr_session.close()

    ls.session.commit()


@router_songs.get(
    "/{song_id}",
    summary="Get a single song.",
    responses={
        **responses.login_error,
        404: {"description": "Song not found"},
    },
    response_model=models.SongOutput
)
def get_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_id: int = f.Path(..., description="The id of the song to be retrieved.")
):
    """
    Get full information for the song with the specified `song_id`.
    """
    return ls.get(tables.Song, song_id)


@router_songs.put(
    "/{song_id}",
    summary="Edit a song.",
    response_model=models.SongOutput,
    responses={
        **responses.login_error,
        404: {"description": "Song not found"},
    }
)
def edit_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_id: int = f.Path(..., description="The id of the song to be edited."),
    data: models.SongInput = f.Body(..., description="The new data the song should have."),
):
    """
    Replace the data of the song with the specified `song_id` with the data passed in the request body.
    """
    song = ls.get(tables.Song, song_id)
    song.update(**data.dict())
    ls.user.log("song.edit.single", obj=song.id)
    ls.session.commit()
    return song


@router_songs.delete(
    "/{song_id}",
    summary="Delete a song.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Song not found"},
    }
)
def delete(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    song_id: int = f.Path(..., description="The id of the song to be deleted.")
):
    """
    Delete the song having the specified `song_id`.

    Note that the contained layers will not be deleted; they will become orphaned instead.
    """
    song = ls.get(tables.Song, song_id)
    ls.session.delete(song)
    ls.user.log("song.delete", obj=song.id)
    ls.session.commit()


__all__ = (
    "router_songs",
)
