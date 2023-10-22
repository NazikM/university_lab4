from fastapi import APIRouter, Cookie, HTTPException
from fastapi.requests import Request

from app.utils.auth import decode_jwt_token

router = APIRouter()


@router.get("/")
async def root(request: Request, token: str = Cookie(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Token not provided")

    try:
        res = decode_jwt_token(token)
        return {"message": f"Hello {res['email']}"}
    except:
        return {"message": "Token not valid. Please login"}
