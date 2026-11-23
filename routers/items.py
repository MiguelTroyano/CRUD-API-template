from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

from auth import get_current_user
from database import get_session
from models import User, Item
from schemas import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)):
    """Create an item owned by the current user."""
    item = Item(
        title = data.title,
        user_id = user.id
    )

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("", response_model=list[ItemRead])
def list_items(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """List the current user's items."""
    return session.exec(select(Item).where(Item.user_id == user.id)).all()


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int,
                data: ItemUpdate,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)):
    """Update only the fields sent in the request (PATCH-like semantics)."""
    item = session.get(Item, item_id)

    # Other users' items also return 404, so their existence is not revealed.
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)):
    """Delete one of the current user's items."""
    item = session.get(Item, item_id)

    if not item or item.user_id != user.id:
        raise HTTPException(404, detail=f"Could not delete item with id {item_id} because it does not exist")

    session.delete(item)
    session.commit()

    return None
