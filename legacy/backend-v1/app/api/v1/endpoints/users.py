from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_user, crud_interaction, crud_playlist
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.interaction import InteractionWithContent
from app.schemas.playlist import Playlist

router = APIRouter()

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.create_user(db, user=user_in)
    return user

@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update current user.
    """
    try:
        user = crud_user.update_user(db, db_obj=current_user, obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/follow", response_model=User)
def follow_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user_to_follow = crud_user.get_user(db, user_id=user_id)
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    if user_to_follow.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")
    
    return crud_user.follow_user(db, current_user, user_to_follow)

@router.post("/{user_id}/unfollow", response_model=User)
def unfollow_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    user_to_unfollow = crud_user.get_user(db, user_id=user_id)
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud_user.unfollow_user(db, current_user, user_to_unfollow)

@router.get("/me/interactions", response_model=List[InteractionWithContent])
def read_user_interactions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user interactions.
    """
    interactions = crud_interaction.get_interactions_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return interactions

@router.get("/me/following", response_model=List[User])
def read_user_following(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get users followed by current user.
    """
    return current_user.followed

@router.get("/me/followers", response_model=List[User])
def read_user_followers(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get users following current user.
    """
    return current_user.followers

@router.get("/{user_id}/following", response_model=List[User])
def read_other_user_following(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get users followed by a specific user.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.followed

@router.get("/{user_id}/followers", response_model=List[User])
def read_other_user_followers(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get users following a specific user.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.followers

@router.get("/search", response_model=List[User])
def search_users(
    query: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
):
    """
    Search users by username.
    """
    return crud_user.search_users(db, query=query, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/interactions", response_model=List[InteractionWithContent])
def read_other_user_interactions(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get interactions of a specific user. Only if following.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if current_user follows user_id
    is_following = any(u.id == user_id for u in current_user.followed)
    if not is_following and current_user.id != user_id:
        return [] # Return empty list if not following

    interactions = crud_interaction.get_interactions_by_user(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return interactions

@router.get("/{user_id}/playlists", response_model=List[Playlist])
def read_other_user_playlists(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get playlists of a specific user. Only if following.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if current_user follows user_id
    is_following = any(u.id == user_id for u in current_user.followed)
    if not is_following and current_user.id != user_id:
        return [] # Return empty list if not following

    playlists = crud_playlist.get_user_playlists(db=db, user_id=user_id, skip=skip, limit=limit)
    return playlists
