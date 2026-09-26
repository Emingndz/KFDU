from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Association table for followers
followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('user.id'), primary_key=True)
)

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    # Relationships
    followed = relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref='followers'
    )
    
    interactions = relationship("Interaction", back_populates="user")
    playlists = relationship("Playlist", back_populates="user")

    @property
    def followers_count(self):
        return len(self.followers)

    @property
    def following_count(self):
        return len(self.followed)
