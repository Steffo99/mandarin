import fastapi as f
import pkg_resources
import uvicorn

from mandarin import database
from mandarin.config import lazy_config
from .description import description
from ...routes import *

app = f.FastAPI(
    debug=True,
    title="Mandarin [DEBUG]",
    description=description,
    version=pkg_resources.get_distribution("mandarin").version,
)
app.include_router(router_version, prefix="/version", tags=["Version"])
app.include_router(router_debug, prefix="/debug", tags=["Debug"])
app.include_router(router_auth, prefix="/auth", tags=["Authentication"])
app.include_router(router_search, prefix="/search", tags=["Search"])
app.include_router(router_files, prefix="/files", tags=["Files"])
app.include_router(router_layers, prefix="/layers", tags=["Layers"])
app.include_router(router_songs, prefix="/songs", tags=["Songs"])
app.include_router(router_albums, prefix="/albums", tags=["Albums"])
app.include_router(router_genres, prefix="/genres", tags=["Genres"])
app.include_router(router_people, prefix="/people", tags=["People"])
app.include_router(router_auditlogs, prefix="/audit-logs", tags=["Audit Logs"])


if __name__ == "__main__":
    database.create_all()
    uvicorn.run(app, port=lazy_config.e["apps.files.port"])
