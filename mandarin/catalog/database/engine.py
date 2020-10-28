from royalnet.typing import *
import sqlalchemy

from .base import Base
from .tables import *


engine: sqlalchemy.engine.Engine = sqlalchemy.create_engine("postgresql://steffo@/mandarin_dev")
Base.metadata.bind = engine
Base.metadata.create_all()
breakpoint()
Base.metadata.drop_all()
