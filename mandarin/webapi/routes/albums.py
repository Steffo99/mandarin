from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import *
from ..models import *
from ..dependencies import *

router_albums = f.APIRouter()


@router_albums.get(
    "/",
    summary="Get all albums.",
    responses={
        **login_error,
    },
    response_model=List[MAlbum]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    return ls.session.query(Album).order_by(Album.id).limit(limit).offset(offset).all()


@router_albums.post(
    "/",
    summary="Create a new album.",
    responses={
        **login_error,
    },
    response_model=MAlbumFull,
)
def create(
    ls: LoginSession = f.Depends(dependency_login_session),
    data: MAlbumWithoutId = f.Body(..., description="The data the new album should have."),
):
    album = Album(**data.__dict__)
    ls.session.add(data)
    ls.session.commit()
    ls.user.log("album.create", obj=album.id)
    ls.session.commit()
    return album


@router_albums.get(
    "/count",
    summary="Get the number of albums currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
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
    Non-existing album_ids will be ignored.
    """
    role = ls.get(Role, role_id)
    person = ls.get(Person, person_id)
    for album in ls.group(Album, album_ids):
        AlbumInvolvement.make(session=ls.session, role=role, album=album, person=person)
        ls.user.log("album.edit.multiple.involve", obj=album.id)
    ls.session.commit()


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
    Non-existing album_ids will be ignored.
    """
    role = ls.get(Role, role_id)
    person = ls.get(Person, person_id)
    for song in ls.group(Album, album_ids):
        AlbumInvolvement.unmake(session=ls.session, role=role, song=song, person=person)
        ls.user.log("album.edit.multiple.uninvolve", obj=song.id)
    ls.session.commit()


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
    Non-existing album_ids will be ignored.
    """
    genre = ls.get(Genre, genre_id)
    for album in ls.group(Album, album_ids):
        album.genres.append(genre)
        ls.user.log("album.edit.multiple.classify", obj=album.id)
    ls.session.commit()


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
    Non-existing album_ids will be ignored.
    """
    genre = ls.get(Genre, genre_id)
    for album in ls.group(Album, album_ids):
        album.genres.remove(genre)
        ls.user.log("album.edit.multiple.declassify", obj=album.id)
    ls.session.commit()


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
    The first album will be used as base and will keep its data.
    """

    if len(album_ids) < 2:
        raise f.HTTPException(400, "Not enough albums specified")

    # Create a new session in SERIALIZABLE isolation mode, so nothing can be added to the genres to be merged.
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Get the first genre
    main_album = rr_session.query(Album).get(album_ids[0])
    ls.user.log("album.merge.to", obj=main_album.id)

    # Get the other genres
    other_albums = rr_session.query(Album).filter(Album.id.in_(album_ids[1:])).all()

    # Replace and delete the other genres
    for merged_album in other_albums:
        for song in merged_album.songs:
            song.album = main_album
        ls.user.log("album.merge.from", obj=merged_album.id)
        rr_session.delete(merged_album)

    rr_session.commit()
    rr_session.close()

    ls.session.commit()


@router_albums.get(
    "/{album_id}",
    summary="Get a single album.",
    responses={
        **login_error,
        404: {"description": "Album not found"},
    },
    response_model=MAlbumFull
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_id: int = f.Path(..., description="The id of the album to be retrieved.")
):
    return ls.get(Album, album_id)


@router_albums.put(
    "/{album_id}",
    summary="Edit an album.",
    response_model=MAlbumFull,
    responses={
        **login_error,
        404: {"description": "Album not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    album_id: int = f.Path(..., description="The id of the album to be edited."),
    data: MAlbumWithoutId = f.Body(..., description="The new data the album should have."),
):
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
    Calling this method WON'T delete the corresponding tracks!
    """
    album = ls.get(Album, album_id)
    ls.session.delete(album)
    ls.user.log("album.delete", obj=album.id)
    ls.session.commit()


__all__ = (
    "router_albums",
)
