from sqlmodel import SQLModel, Field
from pydantic import field_validator

# -- Item ---
class ItemBase(SQLModel):
    """
    Defines the title as the base attribute: REQUIRED and AT LEAST 1 CHARACTER long (not every class will use this base).
    """
    title: str = Field(min_length=1, max_length=100)        # min_length protects against empty titles, but not against titles made only of spaces ("  ")

    """
    The title MUST be marked as required (not typed as None), because the class that defines the SQL table
    inherits from this class.
    This makes the table column "NOT NULL", which protects the database from corrupt inserts made from
    anywhere other than the API endpoints.
    """

    # filter for fields going into the DB and for searches (not applied to reads)
    @field_validator("title", mode="before")      # mode="before": applies the changes before the rest of the Field constraints are checked
    @classmethod
    def strip_title(cls, v):
        """
        If a string was given, strips the spaces at the beginning and the end.
        """
        if isinstance(v, str):
            return v.strip()
        return v
    """
    You could use mode="after" instead and manually check that at least 1 letter is left, raising a ValueError
    otherwise to reproduce the same rejection of the request.
    """

class Item(ItemBase, table=True):
    """
    Class that defines the attributes stored in the DB table
    """
    id: int = Field(default = None, primary_key=True)       # attributes with a default are NOT REQUIRED TO BE PROVIDED, as far as Pydantic is concerned.
    done: bool = False                                      # to make an attribute optional in the DB, it has to be typed as possibly None.
    user_id: int = Field(foreign_key= "user.id")



# --- User ---

# To keep the code reusable, validation functions can be defined outside the class.
def normalize_username(v):
    if isinstance(v, str):
        return v.strip().lower()        # we want every username normalized to lowercase to avoid inconsistencies and confusion
    return v

class UserBase(SQLModel):
    """
    Defines the username as a UNIQUE, indexed attribute.
    """
    username: str = Field(unique = True, index=True, min_length=3, max_length=128, schema_extra={"pattern": r"^[a-zA-Z0-9_]+$"})
    """
    - max_length is used both to validate requests and to define the column type in the
        DB (VARCHAR(max_length))

    - Usernames may only contain letters, numbers and underscores.
        This prevents two users from being treated as different when the only difference is a space or an emoji ("ana" and "a na").
        This constraint is applied only by the API, not by the DB.
    """

    @field_validator("username", mode="before")
    @classmethod
    def _normalize(cls, v):
        return normalize_username(v)
    """
    Note: there are vulnerabilities such as the Cyrillic letter "a", which looks exactly like the regular "a"
    but is considered a different character.
    """

class User(UserBase, table=True):
    id: int = Field(default = None, primary_key=True)
    hashed_password: str
