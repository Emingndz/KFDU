from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.content import Content

class PlaylistBase(BaseModel):
    title: str
    description: Optional[str] = None

class PlaylistCreate(PlaylistBase):
    pass

class PlaylistUpdate(PlaylistBase):
    pass

class Playlist(PlaylistBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[Content] = []

    class Config:
        from_attributes = True
