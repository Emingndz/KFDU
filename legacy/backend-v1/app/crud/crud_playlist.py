from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.playlist import Playlist
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate
from app.models.content import Content

def get_playlist(db: Session, playlist_id: int):
    return db.query(Playlist).filter(Playlist.id == playlist_id).first()

def get_user_playlists(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Playlist).filter(Playlist.user_id == user_id).offset(skip).limit(limit).all()

def create_playlist(db: Session, playlist: PlaylistCreate, user_id: int):
    db_playlist = Playlist(**playlist.dict(), user_id=user_id)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

def add_content_to_playlist(db: Session, playlist: Playlist, content: Content):
    if content not in playlist.items:
        playlist.items.append(content)
        db.commit()
        db.refresh(playlist)
    return playlist

def remove_content_from_playlist(db: Session, playlist: Playlist, content: Content):
    if content in playlist.items:
        playlist.items.remove(content)
        db.commit()
        db.refresh(playlist)
    return playlist

def delete_playlist(db: Session, playlist_id: int):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if playlist:
        db.delete(playlist)
        db.commit()
    return playlist
