import fastapi as f
import uvicorn

from ..database import *
from .auth import *


app = f.FastAPI()


@app.get("/auth/access_token")
def access_token(payload: dict = f.Depends(validate_access_token)):
    return payload


@app.get("/auth/current_user")
def current_user(user: User = f.Depends(find_or_create_user)):
    return f"{user}"


if __name__ == "__main__":
    Base.metadata.create_all()
    uvicorn.run(app, port=30009)
