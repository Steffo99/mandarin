from __future__ import annotations
from royalnet.typing import *
import fastapi as f
import sqlalchemy.orm.session

from ...database import *
from ..models.parse import *
from ..utils.auth import *
from ..utils.upload import *


router_upload = f.APIRouter()


@router_upload.post("/new", summary="Upload a audio track.")
def new(user: User = f.Depends(find_or_create_user), file: f.UploadFile = f.File(...)):
    """
    Upload a new audio track.

    If the metadata matches a song that already exists, add it as a new layer for that song.

    If the metadata does not match any existant song, create a new song (and eventually album), and add the first
    layer to it.
    """

    # Ensure at least a song was uploaded
    if file is None:
        raise f.HTTPException(500, "No file was uploaded")

    # Parse and save the file
    parse, file = save_uploadfile(file, uploader=user)

    # Create a new session in REPEATABLE READ isolation mode, so albums cannot be created twice
    # (*ahem* Funkwhale *ahem*)
    session: sqlalchemy.orm.session.Session = Session()
    session.connection(execution_options={"isolation_level": "REPEATABLE READ"})

    # Add the file to the session
    session.add(file)

    # Use the first parse to create the metadata
    song = auto_song(session=session, parse=parse)

    # Create the layers
    session.add(SongLayer(song=song, file=file))

    # Commit the changes in the session
    session.commit()
    session.close()


__all__ = (
    "router_upload",
)
