from models import UserBase, ItemBase, normalize_username
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class ItemCreate(ItemBase):
    """
    Class with the information the user provides about a new item.
    """
    pass                                                #(same attributes as ItemBase (title))


class ItemRead(ItemBase):
    """
    Class with the information the API returns about the items it handles
    """
    id: int         # needed so the front-end can send PUT and DELETE requests
    done: bool      # needed for the PUT operation
    """
    user_id isn't needed for any operation (the back-end works it out from the token sent with the request).
    So, even though including it wouldn't be a threat, since it isn't needed it's better to leave it out.
    Still, if we ever added an operation where the front-end needed to know the item's owner in advance,
    we would have to include it.
    """


class ItemUpdate(SQLModel):
    """
    Class with the information a user may provide to modify an item.
    """
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None
    """
    We can't inherit the title from the base class, because there it's marked as required, and in partial
    updates it may be left out.
    """

    @field_validator("title", mode="before")      # mode="before": applies the changes before the rest of the Field constraints are checked
    @classmethod
    def strip_title(cls, v):
        """
        If a string was given, strips the spaces at the beginning and the end.
        """
        if isinstance(v, str):
            return v.strip()
        return v


class UserRegister(UserBase):
    """
    Class with the information the user provides about their new account.
    """
    password: str = Field(min_length=8, max_length=128)         # any POST with a password shorter than 8 characters returns 422 (the error code for badly formatted requests).


class UserLogin(SQLModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    """
    When logging in, the only constraint that should be applied to the password entered is one that will
    ALWAYS be applied to newly created ones.
    Maybe in the future the minimum password length goes from 8 to 12. In that case, Login and Register
    can't share the same constraint, because Login would break for users who registered under the old
    rules.

    Also, raising the same error at login as at registration would give whoever is logging in information
    that is only relevant when creating an account (the creation constraints).
    """

    @field_validator("username", mode="before")
    @classmethod
    def _normalize(cls, v):
        return normalize_username(v)


class UserRead(UserBase):
    """
    Class with the information the API returns about the users it handles
    """
    pass        # username (inherited) is all the front-end needs today. The id will be added when it's needed.
