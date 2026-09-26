from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_playlist, crud_content
from app.schemas.playlist import Playlist, PlaylistCreate
from app.models.user import User
from app.services import tmdb_service, book_service
from app.schemas.content import ContentCreate

router = APIRouter()

@router.post("/", response_model=Playlist)
def create_playlist(
    *,
    db: Session = Depends(deps.get_db),
    playlist_in: PlaylistCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new playlist.
    """
    playlist = crud_playlist.create_playlist(db=db, playlist=playlist_in, user_id=current_user.id)
    return playlist

@router.get("/me", response_model=List[Playlist])
def read_user_playlists(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user playlists.
    """
    playlists = crud_playlist.get_user_playlists(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return playlists

@router.get("/{playlist_id}", response_model=Playlist)
def read_playlist(
    playlist_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get playlist by ID.
    """
    playlist = crud_playlist.get_playlist(db=db, playlist_id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    # Allow if owner OR if following the owner
    is_owner = playlist.user_id == current_user.id
    is_following = any(u.id == playlist.user_id for u in current_user.followed)
    
    if not is_owner and not is_following:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return playlist

@router.post("/{playlist_id}/items", response_model=Playlist)
def add_item_to_playlist(
    playlist_id: int,
    external_id: str,
    content_type: str, # 'movie' or 'book'
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add item to playlist.
    """
    playlist = crud_playlist.get_playlist(db=db, playlist_id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Check if content exists locally
    content = crud_content.get_content_by_external_id(db, external_id=external_id, content_type=content_type)
    
    if not content:
        # Fetch details and create content
        if content_type == 'movie':
            details = tmdb_service.get_movie_details(int(external_id))
            if not details:
                raise HTTPException(status_code=404, detail="Movie not found")
            content_in = ContentCreate(
                external_id=str(details['id']),
                content_type="movie",
                title=details.get('title'),
                poster_path=details.get('poster_path'),
                overview=details.get('overview'),
                metadata_content=details
            )
        elif content_type == 'book':
            details = book_service.get_book_details(external_id)
            if not details:
                raise HTTPException(status_code=404, detail="Book not found")
            volume_info = details.get('volumeInfo', {})
            content_in = ContentCreate(
                external_id=details['id'],
                content_type="book",
                title=volume_info.get('title'),
                poster_path=volume_info.get('imageLinks', {}).get('thumbnail'),
                overview=volume_info.get('description'),
                metadata_content=details
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")
            
        content = crud_content.create_content(db, content_in)

    playlist = crud_playlist.add_content_to_playlist(db, playlist, content)
    return playlist

@router.delete("/{playlist_id}/items/{content_id}", response_model=Playlist)
def remove_item_from_playlist(
    playlist_id: int,
    content_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Remove item from playlist.
    """
    playlist = crud_playlist.get_playlist(db=db, playlist_id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    content = db.query(crud_content.Content).filter(crud_content.Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
        
    playlist = crud_playlist.remove_content_from_playlist(db, playlist, content)
    return playlist
