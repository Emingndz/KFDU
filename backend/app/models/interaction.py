from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Interaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    
    rating = Column(Float, nullable=True) # 1-10
    review_text = Column(String, nullable=True)
    status = Column(String, nullable=True) # 'watched', 'reading', etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="interactions")
    content = relationship("Content")
    
    # Activity relationships
    likes = relationship("ActivityLike", back_populates="interaction", cascade="all, delete-orphan")
    comments = relationship("ActivityComment", back_populates="interaction", cascade="all, delete-orphan", order_by="ActivityComment.created_at")

