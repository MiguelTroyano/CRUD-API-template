from models import UserBase, ItemBase, normalize_username
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class ItemCreate(ItemBase):
    """Payload for creating an item."""
    pass


class ItemRead(ItemBase):
    """Item as returned by the API."""
    id: int
    done: bool


class ItemUpdate(SQLModel):
    """Partial update payload: only the fields that are sent get changed."""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        """Strip surrounding whitespace before the length constraints are checked."""
        if isinstance(v, str):
            return v.strip()
        return v


class UserRegister(UserBase):
    """Payload for registering a user."""
    password: str = Field(min_length=8, max_length=128)


class UserLogin(SQLModel):
    """Login payload.

    Registration length rules are deliberately not applied here, so tightening
    them in the future never locks out existing users.
    """
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @field_validator("username", mode="before")
    @classmethod
    def _normalize(cls, v):
        return normalize_username(v)


class UserRead(UserBase):
    """User as returned by the API."""
    pass
