from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from sqlmodel import Session

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_session
from models import User

security = HTTPBearer()

# Argon2 with the library's recommended parameters.
password_hash = PasswordHash.recommended()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
) -> User:
    """FastAPI dependency: resolve the user from the Bearer token or raise 401."""
    token = credentials.credentials

    # One generic error for every failure, so the exact reason is not leaked.
    unauthorized = HTTPException(status_code= 401, detail= "Access denied")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        if user_id is None:
            raise unauthorized

    except jwt.InvalidTokenError:
        raise unauthorized

    user = session.get(User, int(user_id))

    if user is None:
        raise unauthorized
    return user


def create_token(user_id: int):
    """Create a signed JWT for the user that expires after the configured time."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires}
    return jwt.encode(payload= payload, key= SECRET_KEY, algorithm= ALGORITHM)
