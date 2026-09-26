from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def follow_user(db: Session, db_user: User, user_to_follow: User):
    db_user.followed.append(user_to_follow)
    db.commit()
    db.refresh(db_user)
    return db_user

def unfollow_user(db: Session, db_user: User, user_to_unfollow: User):
    db_user.followed.remove(user_to_unfollow)
    db.commit()
    db.refresh(db_user)
    return db_user

def search_users(db: Session, query: str, skip: int = 0, limit: int = 10):
    return db.query(User).filter(User.username.contains(query)).offset(skip).limit(limit).all()

def update_user(db: Session, db_obj: User, obj_in: UserUpdate):
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    # Handle email update - check if already exists
    if update_data.get("email") and update_data["email"] != db_obj.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise ValueError("Bu e-posta adresi zaten kullanımda")

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
