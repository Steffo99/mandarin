import fastapi as f
import uvicorn

from ...database import *
from ...config import *
from ...webapi.routes import *


app = f.FastAPI()
app.include_router(router_auth, prefix="/auth", tags=["auth"])
app.include_router(router_upload, prefix="/upload", tags=["upload"])
app.include_router(router_metadata, prefix="/metadata", tags=["metadata"])


if __name__ == "__main__":
    Base.metadata.drop_all()
    Base.metadata.create_all()
    uvicorn.run(app, port=config["apps.files.port"])
