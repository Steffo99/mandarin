from royalnet.typing import *
import pydantic


class MandarinModel(pydantic.BaseModel):
    class Config(pydantic.BaseModel.Config):
        pass


class OrmModel(MandarinModel):
    class Config(MandarinModel.Config):
        orm_mode = True


__all__ = (
    "MandarinModel",
    "OrmModel",
)
