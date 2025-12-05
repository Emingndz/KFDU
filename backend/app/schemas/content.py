from typing import Optional, Dict, Any
from pydantic import BaseModel

class ContentBase(BaseModel):
    external_id: str
    content_type: str
    title: str
    poster_path: Optional[str] = None
    overview: Optional[str] = None
    metadata_content: Optional[Dict[str, Any]] = None

class ContentCreate(ContentBase):
    pass

class Content(ContentBase):
    id: int

    class Config:
        from_attributes = True
