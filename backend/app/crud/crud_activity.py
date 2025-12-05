from sqlalchemy.orm import Session
from app.models.activity import ActivityLike, ActivityComment
from app.models.interaction import Interaction


def get_like(db: Session, user_id: int, interaction_id: int):
    return db.query(ActivityLike).filter(
        ActivityLike.user_id == user_id,
        ActivityLike.interaction_id == interaction_id
    ).first()


def create_like(db: Session, user_id: int, interaction_id: int):
    db_like = ActivityLike(user_id=user_id, interaction_id=interaction_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like


def delete_like(db: Session, like: ActivityLike):
    db.delete(like)
    db.commit()


def get_likes_count(db: Session, interaction_id: int):
    return db.query(ActivityLike).filter(ActivityLike.interaction_id == interaction_id).count()


def get_comments(db: Session, interaction_id: int, skip: int = 0, limit: int = 50):
    return db.query(ActivityComment).filter(
        ActivityComment.interaction_id == interaction_id
    ).order_by(ActivityComment.created_at.asc()).offset(skip).limit(limit).all()


def create_comment(db: Session, user_id: int, interaction_id: int, text: str):
    db_comment = ActivityComment(user_id=user_id, interaction_id=interaction_id, text=text)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment_by_id(db: Session, comment_id: int):
    return db.query(ActivityComment).filter(ActivityComment.id == comment_id).first()


def delete_comment(db: Session, comment: ActivityComment):
    db.delete(comment)
    db.commit()


def get_comments_count(db: Session, interaction_id: int):
    return db.query(ActivityComment).filter(ActivityComment.interaction_id == interaction_id).count()


def get_interaction_by_id(db: Session, interaction_id: int):
    return db.query(Interaction).filter(Interaction.id == interaction_id).first()


def get_interactions_by_content(db: Session, content_id: int, skip: int = 0, limit: int = 50):
    """Get all interactions for a specific content (for content reviews section)"""
    return db.query(Interaction).filter(
        Interaction.content_id == content_id,
        Interaction.review_text.isnot(None)
    ).order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()


def get_content_average_rating(db: Session, content_id: int):
    """Get average rating for a content"""
    from sqlalchemy import func
    result = db.query(func.avg(Interaction.rating)).filter(
        Interaction.content_id == content_id,
        Interaction.rating.isnot(None)
    ).scalar()
    return round(result, 1) if result else None


def get_content_rating_count(db: Session, content_id: int):
    """Get total rating count for a content"""
    return db.query(Interaction).filter(
        Interaction.content_id == content_id,
        Interaction.rating.isnot(None)
    ).count()
