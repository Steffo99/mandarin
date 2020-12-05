from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import tables, lazy_Session
from ...taskbus import tasks
from .. import models
from .. import dependencies
from .. import responses

router_people = f.APIRouter()


@router_people.get(
    "/",
    summary="Get all people.",
    responses={
        **responses.login_error,
    },
    response_model=List[models.Person]
)
def get_all(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0, le=500),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    """
    Get an array of all the people currently in the database, in pages of `limit` elements and starting at the
    element number `offset`.

    To avoid denial of service attacks, `limit` cannot be greater than 500.
    """
    return ls.session.query(tables.Person).order_by(tables.Person.id).limit(limit).offset(offset).all()


@router_people.post(
    "/",
    summary="Create a new person.",
    responses={
        **responses.login_error,
    },
    response_model=models.PersonOutput,
)
def create(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    data: models.PersonInput = f.Body(..., description="The new data the person should have."),
):
    """
    Create a new person with the data specified in the body of the request.
    """
    person = tables.Person(**data.__dict__)
    ls.session.add(person)
    ls.session.commit()
    ls.user.log("person.create", obj=person.id)
    ls.session.commit()
    return person


@router_people.get(
    "/count",
    summary="Get the total number of people.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependencies.dependency_db_session)
):
    """
    Get the total number of people.

    Since it doesn't require any login, it can be useful to display some information on an "instance preview" page.
    """
    return session.query(tables.Genre).count()


@router_people.patch(
    "/merge",
    summary="Merge two or more people.",
    status_code=204,
    responses={
        **responses.login_error,
        400: {"description": "Not enough people specified"}
    },
)
def merge(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    ss: sqlalchemy.orm.Session = f.Depends(dependencies.dependency_db_session_serializable),
    people_ids: List[int] = f.Query(..., description="The ids of the people to merge."),
):
    """
    Change the involvements of all the passed people to involve the first person instead, then delete the now-empty
    people from the second to the last place.
    """

    if len(people_ids) < 2:
        raise f.HTTPException(400, "Not enough people specified")

    # Get the first genre
    main_person = ss.query(tables.Person).get(people_ids[0])
    ls.user.log("person.merge.to", obj=main_person.id)

    # Get the other genres
    other_people = ss.query(tables.Person).filter(tables.Person.id.in_(people_ids[1:])).all()

    # Replace and delete the other genres
    for merged_person in other_people:
        for song_involvement in merged_person.song_involvements:
            song_involvement.person = main_person
        for album_involvement in merged_person.album_involvements:
            album_involvement.person = main_person
        ls.user.log("person.merge.from", obj=merged_person.id)
        ss.delete(merged_person)

    ss.commit()
    ss.close()

    ls.session.commit()
    return f.Response(status_code=204)


@router_people.get(
    "/{person_id}",
    summary="Get a single person.",
    responses={
        **responses.login_error,
        404: {"description": "Person not found"},
    },
    response_model=models.PersonOutput
)
def get_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    person_id: int = f.Path(..., description="The id of the person to be retrieved."),
):
    """
    Get full information for the person with the specified `person_id`.
    """
    return ls.get(tables.Person, person_id)


@router_people.put(
    "/{person_id}",
    summary="Edit a person.",
    response_model=models.PersonOutput,
    responses={
        **responses.login_error,
        404: {"description": "Person not found"},
    }
)
def edit_single(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    person_id: int = f.Path(..., description="The id of the person to be edited."),
    data: models.PersonInput = f.Body(..., description="The new data the person should have."),
):
    """
    Replace the data of the person with the specified `person_id` with the data passed in the request body.
    """
    person = ls.get(tables.Person, person_id)
    person.update(**data.__dict__)
    ls.user.log("person.edit.single", obj=person.id)
    ls.session.commit()
    return person


@router_people.delete(
    "/{person_id}",
    summary="Delete a person.",
    status_code=204,
    responses={
        **responses.login_error,
        404: {"description": "Person not found"},
    }
)
def delete(
    ls: dependencies.LoginSession = f.Depends(dependencies.dependency_login_session),
    person_id: int = f.Path(..., description="The id of the person to be edited."),
):
    """
    Delete the person having the specified `album_id`.

    All their involvements will be deleted.
    """
    person = ls.get(tables.Person, person_id)
    ls.session.delete(person)
    ls.user.log("person.delete", obj=person.id)
    ls.session.commit()
    return f.Response(status_code=204)


__all__ = (
    "router_people",
)
