from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer

app = APIRouter(prefix="/user", tags=["user"])

__oauth2_scheme__ = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def get_current_user():
    return {"message": "Hello World"}
