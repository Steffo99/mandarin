import uvicorn

from ..database import *
from .database import *
from .app import *
from .routes import *


if __name__ == "__main__":
    Base.metadata.create_all()
    uvicorn.run(app, port=30009)
