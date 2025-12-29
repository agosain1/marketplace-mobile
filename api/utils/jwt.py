import os
import datetime
from jose import jwt, JWTError
from fastapi import Request, Response, HTTPException, status
from sqlalchemy.orm import Session

from models import RefreshTokens

JWT_SECRET = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
ACCESS_TOKEN_MINS = float(os.getenv("ACCESS_TOKEN_MINS"))

def create_access_token(user_id: str):
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": now + datetime.timedelta(minutes=ACCESS_TOKEN_MINS),
        "iat": now
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

def validate_refresh_token(db: Session, request: Request):
    refresh_id = request.cookies.get("refresh_token")
    if not refresh_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    token = db.query(RefreshTokens).filter(RefreshTokens.id == refresh_id).first()

    if not token or token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    expires_at_utc = token.expires_at.replace(tzinfo=datetime.UTC)
    if expires_at_utc < datetime.datetime.now(datetime.UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    return token

def issue_new_access_token(db: Session, request: Request, response: Response):
    token = validate_refresh_token(db, request)

    new_access_token = create_access_token(str(token.user_id))

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * ACCESS_TOKEN_MINS
    )

    return str(token.user_id)