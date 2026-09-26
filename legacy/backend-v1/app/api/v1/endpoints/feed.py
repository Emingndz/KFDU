from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from app.api import deps
from app.models.interaction import Interaction
from app.models.user import User
from app.schemas.interaction import InteractionWithUserAndContent, ActivityCommentCreate, ActivityComment
from app.crud import crud_activity

router = APIRouter()


class CommentCreateRequest(BaseModel):
    text: str


@router.get("/")
def get_feed(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    # Get IDs of users followed by current_user
    followed_ids = [user.id for user in current_user.followed]
    
    if not followed_ids:
        return []

    feed_items = (
        db.query(Interaction)
        .filter(Interaction.user_id.in_(followed_ids))
        .order_by(desc(Interaction.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Enrich with likes/comments count and user_liked status
    result = []
    for item in feed_items:
        likes_count = crud_activity.get_likes_count(db, item.id)
        user_liked = crud_activity.get_like(db, current_user.id, item.id) is not None
        comments = crud_activity.get_comments(db, item.id, limit=50)  # Get all comments
        
        item_dict = {
            "id": item.id,
            "user_id": item.user_id,
            "content_id": item.content_id,
            "rating": item.rating,
            "review_text": item.review_text,
            "status": item.status,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "user": {
                "id": item.user.id,
                "username": item.user.username,
                "email": item.user.email,
                "avatar_url": item.user.avatar_url
            },
            "content": {
                "id": item.content.id,
                "external_id": item.content.external_id,
                "content_type": item.content.content_type,
                "title": item.content.title,
                "poster_path": item.content.poster_path,
                "overview": item.content.overview
            },
            "likes_count": likes_count,
            "user_liked": user_liked,
            "comments": [
                {
                    "id": c.id,
                    "text": c.text,
                    "created_at": c.created_at,
                    "user": {
                        "id": c.user.id,
                        "username": c.user.username,
                        "avatar_url": c.user.avatar_url
                    }
                } for c in comments
            ]
        }
        result.append(item_dict)
    
    return result


@router.post("/interactions/{interaction_id}/like")
def like_interaction(
    interaction_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Like an interaction"""
    interaction = crud_activity.get_interaction_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Etkileşim bulunamadı")
    
    existing_like = crud_activity.get_like(db, current_user.id, interaction_id)
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Zaten beğendiniz")
    
    crud_activity.create_like(db, current_user.id, interaction_id)
    return {"liked": True, "likes_count": crud_activity.get_likes_count(db, interaction_id)}


@router.delete("/interactions/{interaction_id}/like")
def unlike_interaction(
    interaction_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Unlike an interaction"""
    interaction = crud_activity.get_interaction_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Etkileşim bulunamadı")
    
    existing_like = crud_activity.get_like(db, current_user.id, interaction_id)
    
    if not existing_like:
        raise HTTPException(status_code=400, detail="Beğeni bulunamadı")
    
    crud_activity.delete_like(db, existing_like)
    return {"liked": False, "likes_count": crud_activity.get_likes_count(db, interaction_id)}


@router.post("/interactions/{interaction_id}/comments")
def add_comment(
    interaction_id: int,
    comment_data: CommentCreateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Add a comment to an interaction"""
    interaction = crud_activity.get_interaction_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Etkileşim bulunamadı")
    
    if not comment_data.text or not comment_data.text.strip():
        raise HTTPException(status_code=400, detail="Yorum metni boş olamaz")
    
    comment = crud_activity.create_comment(db, current_user.id, interaction_id, comment_data.text.strip())
    return {
        "id": comment.id,
        "text": comment.text,
        "created_at": comment.created_at,
        "user": {
            "id": comment.user.id,
            "username": comment.user.username,
            "avatar_url": comment.user.avatar_url
        }
    }


@router.delete("/interactions/{interaction_id}/comments/{comment_id}")
def delete_comment(
    interaction_id: int,
    comment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete a comment"""
    comment = crud_activity.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu yorumu silme yetkiniz yok")
    
    crud_activity.delete_comment(db, comment)
    return {"message": "Yorum silindi"}


@router.get("/interactions/{interaction_id}")
def get_interaction_details(
    interaction_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get interaction details including likes and comments"""
    interaction = crud_activity.get_interaction_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Etkileşim bulunamadı")
    
    likes_count = crud_activity.get_likes_count(db, interaction_id)
    user_liked = crud_activity.get_like(db, current_user.id, interaction_id) is not None
    comments = crud_activity.get_comments(db, interaction_id, limit=100)
    
    return {
        "id": interaction.id,
        "user_id": interaction.user_id,
        "content_id": interaction.content_id,
        "rating": interaction.rating,
        "review_text": interaction.review_text,
        "status": interaction.status,
        "created_at": interaction.created_at,
        "user": {
            "id": interaction.user.id,
            "username": interaction.user.username,
            "avatar_url": interaction.user.avatar_url
        },
        "content": {
            "id": interaction.content.id,
            "external_id": interaction.content.external_id,
            "content_type": interaction.content.content_type,
            "title": interaction.content.title,
            "poster_path": interaction.content.poster_path
        },
        "likes_count": likes_count,
        "user_liked": user_liked,
        "comments": [
            {
                "id": c.id,
                "text": c.text,
                "created_at": c.created_at,
                "user": {
                    "id": c.user.id,
                    "username": c.user.username,
                    "avatar_url": c.user.avatar_url
                }
            } for c in comments
        ]
    }


@router.get("/content/{external_id}/interactions")
def get_content_interactions(
    external_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get all interactions for a content with likes and comments"""
    from app.crud import crud_content
    
    content = crud_content.get_content_by_external_id_only(db, external_id)
    if not content:
        # İçerik veritabanında yoksa boş liste döndür
        return []
    
    interactions = db.query(Interaction).filter(Interaction.content_id == content.id).all()
    
    result = []
    for item in interactions:
        likes_count = crud_activity.get_likes_count(db, item.id)
        user_liked = crud_activity.get_like(db, current_user.id, item.id) is not None
        comments = crud_activity.get_comments(db, item.id, limit=50)
        
        result.append({
            "id": item.id,
            "user": {
                "id": item.user.id,
                "username": item.user.username,
                "avatar_url": item.user.avatar_url
            },
            "rating": item.rating,
            "review_text": item.review_text,
            "status": item.status,
            "created_at": item.created_at,
            "likes_count": likes_count,
            "user_liked": user_liked,
            "comments": [
                {
                    "id": c.id,
                    "text": c.text,
                    "created_at": c.created_at,
                    "user": {
                        "id": c.user.id,
                        "username": c.user.username,
                        "avatar_url": c.user.avatar_url
                    }
                } for c in comments
            ]
        })
    
    return result
