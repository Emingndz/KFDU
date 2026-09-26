from sqlalchemy.orm import Session
from app.models.content import Content
from app.schemas.content import ContentCreate

def get_content(db: Session, content_id: int):
    return db.query(Content).filter(Content.id == content_id).first()

def get_content_by_external_id(db: Session, external_id: str, content_type: str):
    return db.query(Content).filter(Content.external_id == external_id, Content.content_type == content_type).first()

def get_content_by_external_id_only(db: Session, external_id: str):
    """Get content by external_id without checking content_type"""
    return db.query(Content).filter(Content.external_id == external_id).first()

def create_content(db: Session, content: ContentCreate):
    db_content = Content(
        external_id=content.external_id,
        content_type=content.content_type,
        title=content.title,
        poster_path=content.poster_path,
        overview=content.overview,
        metadata_content=content.metadata_content
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content
