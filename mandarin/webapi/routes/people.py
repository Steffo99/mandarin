from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from ...database import *
from ..models import *
from ..dependencies import *

router_people = f.APIRouter()


@router_people.get(
    "/",
    summary="Get all people.",
    responses={
        **login_error,
    },
    response_model=List[MPerson]
)
def get_all(
    ls: LoginSession = f.Depends(dependency_login_session),
    limit: int = f.Query(500, description="The number of objects that will be returned.", ge=0),
    offset: int = f.Query(0, description="The starting object from which the others will be returned.", ge=0),
):
    return ls.session.query(Person).order_by(Person.id).limit(limit).offset(offset).all()


@router_people.post(
    "/",
    summary="Create a new person.",
    responses={
        **login_error,
    },
    response_model=MPersonFull,
)
def create(
    ls: LoginSession = f.Depends(dependency_login_session),
    data: MPerson = f.Body(..., description="The new data the person should have."),
):
    person = Person(**data)
    ls.session.add(person)
    ls.session.commit()
    ls.user.log("person.create", obj=person.id)
    ls.session.commit()
    return person


@router_people.get(
    "/count",
    summary="Get the number of people currently in the database.",
    response_model=int,
)
def count(
    session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session)
):
    return session.query(Genre).count()


@router_people.patch(
    "/merge",
    summary="Merge two or more people.",
    status_code=204,
    responses={
        **login_error,
        400: {"description": "Not enough people specified"}
    },
)
def merge(
    ls: LoginSession = f.Depends(dependency_login_session),
    people_ids: List[int] = f.Query(..., description="The ids of the people to merge."),
):
    """
    The first person will be used as base and will keep its name and description.
    """

    if len(people_ids) < 2:
        raise f.HTTPException(400, "Not enough people specified")

    # Create a new session in SERIALIZABLE isolation mode, so nothing can be added to the genres to be merged.
    rr_session: sqlalchemy.orm.session.Session = Session()
    rr_session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    # Get the first genre
    main_person = rr_session.query(Person).get(people_ids[0])
    ls.user.log("person.merge.to", obj=main_person.id)

    # Get the other genres
    other_people = rr_session.query(Person).filter(Person.id.in_(people_ids[1:])).all()

    # Replace and delete the other genres
    for merged_person in other_people:
        for song_involvement in merged_person.song_involvements:
            song_involvement.person = main_person
        for album_involvement in merged_person.album_involvements:
            album_involvement.person = main_person
        ls.user.log("person.merge.from", obj=merged_person.id)
        rr_session.delete(merged_person)

    rr_session.commit()
    rr_session.close()

    ls.session.commit()


@router_people.get(
    "/{person_id}",
    summary="Get a single person.",
    responses={
        **login_error,
        404: {"description": "Person not found"},
    },
    response_model=MPersonFull
)
def get_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    person_id: int = f.Path(..., description="The id of the person to be retrieved."),
):
    return ls.get(Person, person_id)


@router_people.put(
    "/{person_id}",
    summary="Edit a person.",
    response_model=MPersonFull,
    responses={
        **login_error,
        404: {"description": "Person not found"},
    }
)
def edit_single(
    ls: LoginSession = f.Depends(dependency_login_session),
    person_id: int = f.Path(..., description="The id of the person to be edited."),
    data: MPersonWithoutId = f.Body(..., description="The new data the person should have."),
):
    person = ls.get(Person, person_id)
    person.update(**data.__dict__)
    ls.user.log("person.edit.single", obj=person.id)
    ls.session.commit()
    return person


@router_people.delete(
    "/{person_id}",
    summary="Delete a person.",
    status_code=204,
    responses={
        **login_error,
        404: {"description": "Person not found"},
    }
)
def delete(
    ls: LoginSession = f.Depends(dependency_login_session),
    person_id: int = f.Path(..., description="The id of the person to be edited."),
):
    person = ls.get(Person, person_id)
    ls.session.delete(person)
    ls.user.log("person.delete", obj=person.id)
    ls.session.commit()


__all__ = (
    "router_people",
)
