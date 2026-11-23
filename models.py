from sqlmodel import SQLModel, Field
from pydantic import field_validator

# --- Item ---
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        """Strip surrounding whitespace before the length constraints are checked."""
        if isinstance(v, str):
            return v.strip()
        return v

class Item(ItemBase, table=True):
    id: int = Field(default = None, primary_key=True)
    done: bool = False
    user_id: int = Field(foreign_key= "user.id")



# --- User ---

def normalize_username(v):
    """Strip and lowercase usernames so that "Ana" and "ana" are the same user."""
    if isinstance(v, str):
        return v.strip().lower()
    return v

class UserBase(SQLModel):
    # The character pattern is enforced by the API only, not by the database.
    username: str = Field(unique = True, index=True, min_length=3, max_length=128, schema_extra={"pattern": r"^[a-zA-Z0-9_]+$"})

    @field_validator("username", mode="before")
    @classmethod
    def _normalize(cls, v):
        return normalize_username(v)

class User(UserBase, table=True):
    id: int = Field(default = None, primary_key=True)
    hashed_password: str
