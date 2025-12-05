from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .content import Content
from .user import User

class InteractionBase(BaseModel):
    rating: Optional[float] = None
    review_text: Optional[str] = None
    status: Optional[str] = None

class InteractionCreate(InteractionBase):
    content_id: int

class InteractionUpdate(InteractionBase):
    pass

# Activity Like/Comment Schemas
class ActivityLikeBase(BaseModel):
    interaction_id: int

class ActivityLikeCreate(ActivityLikeBase):
    pass

class ActivityLike(ActivityLikeBase):
    id: int
    user_id: int
    created_at: datetime
    user: User
    
    class Config:
        from_attributes = True

class ActivityCommentBase(BaseModel):
    text: str

class ActivityCommentCreate(ActivityCommentBase):
    interaction_id: int

class ActivityComment(ActivityCommentBase):
    id: int
    user_id: int
    interaction_id: int
    created_at: datetime
    user: User
    
    class Config:
        from_attributes = True

class Interaction(InteractionBase):
    id: int
    user_id: int
    content_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InteractionWithContent(Interaction):
    content: Content

class InteractionWithUserAndContent(InteractionWithContent):
    user: 'User'
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    is_liked: Optional[bool] = False
    comments: Optional[List[ActivityComment]] = []

InteractionWithUserAndContent.model_rebuild()
