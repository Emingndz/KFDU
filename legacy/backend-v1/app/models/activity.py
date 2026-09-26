from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class ActivityLike(Base):
    """Likes on feed activities (interactions)"""
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    interaction_id = Column(Integer, ForeignKey("interaction.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    interaction = relationship("Interaction", back_populates="likes")


class ActivityComment(Base):
    """Comments on feed activities (interactions)"""
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    interaction_id = Column(Integer, ForeignKey("interaction.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    interaction = relationship("Interaction", back_populates="comments")
