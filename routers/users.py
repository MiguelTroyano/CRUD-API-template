from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from auth import password_hash, create_token
from database import get_session
from models import User
from schemas import UserRegister, UserLogin, UserRead

router = APIRouter(tags=["users"])       # tags: groups these endpoints in /docs
# No prefix: /register and /login don't share a common URL root.

#Route /register. Always accessed with a POST method, to create a new user.
@router.post("/register", response_model=UserRead)
def register(data: UserRegister,
             session: Session = Depends(get_session)):

    #Check that there is no user with the same name
    existing = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    #Create the user instance
    user = User(
        username = data.username,
        hashed_password= password_hash.hash(data.password)         #We never store the user's literal password
    )

    #Update the DB
    session.add(user)
    session.commit()
    session.refresh(user)

    return user          # Since a response model was declared, only the user fields defined in it are returned (plus extra documentation in /docs)


#Route /login. POST method: an access token is created if the login data is valid.
@router.post("/login")
def login(data: UserLogin,
          session: Session = Depends(get_session)):           #the fields the user enters to register and to log in are the same

    #Check that the user trying to log in exists, and get their hashed password
    user = session.exec(
        select(User).where(User.username == data.username)
    ).first()

    if not user or not password_hash.verify(data.password, user.hashed_password):        #the same error is raised for both reasons, to prevent user enumeration
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    """
    A JWT token has 3 segments: header.payload.signature
    The header contains the algorithm used.
    The payload holds both the user (SUBject) and the token's EXPiration date.
    These two parts are readable by anyone. NEVER PUT CONFIDENTIAL INFORMATION IN THEM. Don't send the username as sub, since it may contain personal data.
    The signature lets you verify where the token came from. The server generates it, and checks it, from the header, the payload and a secret key that only the server knows.
    The token carries its own proof, so the server doesn't store anything.
    There's no sessions table, and no need to query the database to know whether a token is legitimate. It scales well.

    The only risk is a token being stolen, which lets the thief use it as they please. That's why tokens have expiration dates, and why
    both the expiration date and the user's identity are used to build the signature: if an attacker steals a token, they can only use it for a limited time,
    and they can't change its identity (to an admin one, say) or extend its expiration date (because the signature would change).
    """
    token = create_token(user.id)

    return {"access_token": token, "token_type": "bearer"}
