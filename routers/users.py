from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from auth import password_hash, create_token
from database import get_session
from models import User
from schemas import UserRegister, UserLogin, UserRead

router = APIRouter(tags=["users"])


@router.post("/register", response_model=UserRead)
def register(data: UserRegister,
             session: Session = Depends(get_session)):
    """Create a user. Only the password hash is stored."""

    existing = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username = data.username,
        hashed_password= password_hash.hash(data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post("/login")
def login(data: UserLogin,
          session: Session = Depends(get_session)):
    """Return a JWT access token if the credentials are valid."""

    user = session.exec(
        select(User).where(User.username == data.username)
    ).first()

    # Same error for an unknown user and a wrong password, to prevent user enumeration.
    if not user or not password_hash.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_token(user.id)

    return {"access_token": token, "token_type": "bearer"}
