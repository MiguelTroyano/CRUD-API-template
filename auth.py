from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from sqlmodel import Session

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_session
from models import User

security = HTTPBearer()                                 # FastAPI expects a token in the headers.

password_hash = PasswordHash.recommended()
"""
Hasher: Argon2 with default parameters.
Uses different random "data" (a salt) for each user, so two users can have the same password.
Uses deliberately slow hashing algorithms to prevent brute-force attacks.
"""



"""
It's important that the API doesn't directly accept the class that defines the DB tables.
That would let users control things we don't want them to control (like the id of their user or their items,
or their password hash), which could cause unexpected errors or enable attacks.
If an attacker knew the output of your password hash, they could send it as is. This way we force them to know
the original password.
"""


#Authorization function that runs before every endpoint that takes this function as an argument
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
) -> User:
    #Get the token from the headers
    token = credentials.credentials

    #A single error for a token without an owner, an unregistered owner, or an invalid signature or expiration date.
    unauthorized = HTTPException(status_code= 401, detail= "Access denied")

    #Get the id of the user who owns the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])         # raises InvalidTokenError if the signature is invalid or the token has expired

        user_id = payload.get("sub")
        if user_id is None:
            raise unauthorized         # token without an owner

    except jwt.InvalidTokenError:
        raise unauthorized

    #Get the user's data
    user = session.get(User, int(user_id))        # .get(Table, id) is used to find a row by its primary key

    if user is None:
        raise unauthorized     # unregistered user
    return user


def create_token(user_id: int):
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires}
    return jwt.encode(payload= payload, key= SECRET_KEY, algorithm= ALGORITHM)
