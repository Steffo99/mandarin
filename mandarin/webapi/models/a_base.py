"""
Base models are :class:`pydantic.BaseModel` that are subclassed by all other models used by Mandarin.

This allows for quick changes to the configuration of *all* Mandarin models.
"""

from royalnet.typing import *
import pydantic


class MandarinModel(pydantic.BaseModel):
    """
    A model for generic data.
    """

    class Config(pydantic.BaseModel.Config):
        """
        The default :mod:`pydantic` configuration.

        .. seealso:: `Pydantic Configuration <https://pydantic-docs.helpmanual.io/usage/model_config/>`_,
                     :class:`pydantic.BaseModel.Config`
        """
        pass


class OrmModel(MandarinModel):
    """
    A model for :mod:`sqlalchemy` table data.
    """

    class Config(MandarinModel.Config):
        """
        A configuration which allows for the loading of data from ``__getattr__`` instead of ``__getitem__``.

        .. seealso:: `Pydantic ORM Mode <https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary
                     -class-instances>`_
        """
        orm_mode = True


__all__ = (
    "MandarinModel",
    "OrmModel",
)
