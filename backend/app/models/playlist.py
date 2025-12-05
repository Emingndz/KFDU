from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

playlist_items = Table(
    'playlist_items',
    Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlist.id'), primary_key=True),
    Column('content_id', Integer, ForeignKey('content.id'), primary_key=True),
    Column('added_at', DateTime(timezone=True), server_default=func.now())
)

class Playlist(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="playlists")
    items = relationship("Content", secondary=playlist_items)
