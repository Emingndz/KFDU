from sqlalchemy import Column, Integer, String, JSON
from app.db.base_class import Base
import enum

class ContentType(str, enum.Enum):
    movie = "movie"
    book = "book"

class Content(Base):
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True) # ID from TMDb or Google Books
    content_type = Column(String, nullable=False) # 'movie' or 'book'
    title = Column(String, index=True)
    poster_path = Column(String, nullable=True)
    overview = Column(String, nullable=True)
    metadata_content = Column(JSON, nullable=True) # Extra details
