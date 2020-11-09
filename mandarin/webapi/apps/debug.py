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
app.include_router(router_version, prefix="/v0/version", tags=["Version"])
app.include_router(router_auth, prefix="/v0/auth", tags=["Authentication"])
app.include_router(router_upload, prefix="/v0/upload", tags=["Upload"])
app.include_router(router_layers, prefix="/v0/layers", tags=["Layers"])


if __name__ == "__main__":
    Base.metadata.create_all()
    uvicorn.run(app, port=config["apps.files.port"])
