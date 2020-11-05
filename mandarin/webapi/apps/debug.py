import fastapi as f
import uvicorn
import pkg_resources

from ...database import *
from ...config import *
from ...webapi.routes import *


app = f.FastAPI(
    debug=True,
    title="Mandarin [DEBUG]",
    description="A debug endpoint for the Mandarin API.\n\nWARNING: Running this will drop all tables from the "
                "database!",
    version=pkg_resources.get_distribution("mandarin").version,
)
app.include_router(router_auth, prefix="/auth", tags=["Authentication"])
app.include_router(router_upload, prefix="/upload", tags=["Upload"])
app.include_router(router_metadata, prefix="/metadata", tags=["Metadata"])
app.include_router(router_version, prefix="/version", tags=["Version"])


if __name__ == "__main__":
    Base.metadata.drop_all()
    Base.metadata.create_all()
    uvicorn.run(app, port=config["apps.files.port"])
