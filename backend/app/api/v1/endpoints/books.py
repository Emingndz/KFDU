from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.services import book_service
from app.crud import crud_content, crud_interaction, crud_activity
from app.schemas.content import ContentCreate
from app.schemas.interaction import InteractionCreate, Interaction, InteractionUpdate
from app.models.user import User

router = APIRouter()

@router.get("/categories")
def get_book_categories():
    """Get list of book categories for filtering"""
    return book_service.get_book_categories()

@router.get("/discover")
def discover_books(
    page: int = 1,
    category: Optional[str] = None,
    year: Optional[int] = None
):
    """Discover books with filters"""
    return book_service.discover_books(page=page, category=category, year=year)

@router.get("/search")
def search_books(query: str):
    return book_service.search_books(query)

@router.get("/popular")
def get_popular_books(page: int = 1):
    return book_service.get_popular_books(page)

@router.get("/{book_id}")
def get_book_details(book_id: str):
    return book_service.get_book_details(book_id)

@router.get("/{book_id}/platform-stats")
def get_book_platform_stats(
    book_id: str,
    db: Session = Depends(deps.get_db),
):
    """Get platform statistics for a book (average rating, review count)"""
    content = crud_content.get_content_by_external_id(db, external_id=book_id, content_type="book")
    if not content:
        return {"average_rating": None, "rating_count": 0, "reviews": []}
    
    avg_rating = crud_activity.get_content_average_rating(db, content.id)
    rating_count = crud_activity.get_content_rating_count(db, content.id)
    reviews = crud_activity.get_interactions_by_content(db, content.id, limit=10)
    
    return {
        "average_rating": avg_rating,
        "rating_count": rating_count,
        "reviews": [
            {
                "id": r.id,
                "user": {"id": r.user.id, "username": r.user.username, "avatar_url": r.user.avatar_url},
                "rating": r.rating,
                "review_text": r.review_text,
                "created_at": r.created_at.isoformat()
            }
            for r in reviews
        ]
    }

@router.post("/interact", response_model=Interaction)
def interact_with_book(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    external_id: str,
    rating: Optional[float] = None,
    review: Optional[str] = None,
    status: Optional[str] = None
):
    # 1. Check if content exists locally
    content = crud_content.get_content_by_external_id(db, external_id=external_id, content_type="book")
    
    if not content:
        # Fetch details from Google Books to save locally
        details = book_service.get_book_details(external_id)
        if not details:
             raise HTTPException(status_code=404, detail="Book not found")
        
        volume_info = details.get('volumeInfo', {})
        
        content_in = ContentCreate(
            external_id=details['id'],
            content_type="book",
            title=volume_info.get('title'),
            poster_path=volume_info.get('imageLinks', {}).get('thumbnail'),
            overview=volume_info.get('description'),
            metadata_content=details
        )
        content = crud_content.create_content(db, content_in)
    
    # 2. Check/Create/Update interaction
    interaction = crud_interaction.get_interaction(db, user_id=current_user.id, content_id=content.id)
    
    if interaction:
        # Update existing interaction
        update_data = InteractionUpdate(
            rating=rating if rating is not None else interaction.rating,
            review_text=review if review is not None else interaction.review_text,
            status=status if status is not None else interaction.status
        )
        interaction = crud_interaction.update_interaction(db, interaction, update_data)
    else:
        # Create new interaction
        interaction_in = InteractionCreate(
            content_id=content.id,
            rating=rating,
            review_text=review,
            status=status
        )
        interaction = crud_interaction.create_interaction(db, interaction_in, user_id=current_user.id)
        
    return interaction
