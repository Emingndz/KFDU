from sqlalchemy.orm import Session
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate, InteractionUpdate

def get_interaction(db: Session, user_id: int, content_id: int):
    return db.query(Interaction).filter(Interaction.user_id == user_id, Interaction.content_id == content_id).first()

def create_interaction(db: Session, interaction: InteractionCreate, user_id: int):
    db_interaction = Interaction(
        user_id=user_id,
        content_id=interaction.content_id,
        rating=interaction.rating,
        review_text=interaction.review_text,
        status=interaction.status
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

def update_interaction(db: Session, db_obj: Interaction, obj_in: InteractionUpdate):
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_interactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Interaction).filter(Interaction.user_id == user_id).offset(skip).limit(limit).all()
