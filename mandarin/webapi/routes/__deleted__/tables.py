from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm

from mandarin.database import *
from mandarin.webapi.models.database import *
from mandarin.webapi.dependencies import *


router_tables = f.APIRouter()


def editable(table_type, input_model, response_model):
    @router_tables.post(
        f"/{table_type.__tablename__}",
        summary=f"Create a new {table_type.__name__}.",
        response_model=response_model,
        responses={
            **login_error,
        },
    )
    def post(
        model: input_model = f.Body(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        obj = table_type(**model)
        session.add(obj)
        session.commit()
        return response_model.from_orm(obj)

    @router_tables.patch(
        f"/{table_type.__tablename__}",
        summary=f"Edit multiple {table_type.__name__}s.",
        response_model=List[response_model],
        responses={
            **login_error,
        },
    )
    def patch(
        ids: List[int] = f.Query(...),
        model: dict = f.Body(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        objs = session.query(table_type).filter(table_type.id.in_(ids)).all()

        for obj in objs:
            obj.update(**{key: value for key, value in model.items() if not (key == "id" or key.startswith("_"))})
        session.commit()

        return [response_model.from_orm(obj) for obj in objs]

    @router_tables.delete(
        f"/{table_type.__tablename__}",
        summary=f"Delete multiple {table_type.__name__}s.",
        status_code=204,
        responses={
            **login_error,
        },
    )
    def delete(
        ids: List[int] = f.Query(...),
        user: User = f.Depends(dependency_valid_user),
        session: sqlalchemy.orm.session.Session = f.Depends(dependency_db_session),
    ):
        objs = session.query(table_type).filter(table_type.id.in_(ids)).all()

        for obj in objs:
            session.delete(obj)
        session.commit()

    return post, patch, delete


editable(AlbumRole, MAlbumRoleWithoutId, MAlbumRole)
editable(Album, MAlbumWithoutId, MAlbum)
editable(Genre, MGenreWithoutId, MGenre)
editable(Person, MPersonWithoutId, MPerson)
editable(SongRole, MSongRoleWithoutId, MSongRole)
editable(Song, MSongWithoutId, MSong)


__all__ = (
    "router_tables",
)
