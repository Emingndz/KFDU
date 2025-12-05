from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.services import tmdb_service
from app.crud import crud_content, crud_interaction, crud_activity
from app.schemas.content import ContentCreate
from app.schemas.interaction import InteractionCreate, Interaction, InteractionUpdate, InteractionWithUserAndContent
from app.models.user import User

router = APIRouter()

@router.get("/search")
def search_movies(query: str):
    return tmdb_service.search_movies(query)

@router.get("/popular")
def get_popular_movies(page: int = 1):
    return tmdb_service.get_popular_movies(page)

@router.get("/genres")
def get_movie_genres():
    """Get list of movie genres"""
    return tmdb_service.get_movie_genres()

@router.get("/discover")
def discover_movies(
    page: int = 1,
    genre: Optional[int] = None,
    year: Optional[int] = None,
    sort_by: str = "popularity.desc"
):
    """Discover movies with filters"""
    return tmdb_service.discover_movies(page=page, genre=genre, year=year, sort_by=sort_by)

@router.get("/{movie_id}")
def get_movie_details(movie_id: int):
    return tmdb_service.get_movie_details(movie_id)

@router.get("/{movie_id}/platform-stats")
def get_movie_platform_stats(
    movie_id: int,
    db: Session = Depends(deps.get_db),
):
    """Get platform statistics for a movie (average rating, review count)"""
    content = crud_content.get_content_by_external_id(db, external_id=str(movie_id), content_type="movie")
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
def interact_with_movie(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    external_id: str,
    rating: Optional[float] = None,
    review: Optional[str] = None,
    status: Optional[str] = None
):
    # 1. Check if content exists locally
    content = crud_content.get_content_by_external_id(db, external_id=external_id, content_type="movie")
    
    if not content:
        # Fetch details from TMDb to save locally
        details = tmdb_service.get_movie_details(int(external_id))
        if not details:
             raise HTTPException(status_code=404, detail="Movie not found in TMDb")
        
        content_in = ContentCreate(
            external_id=str(details['id']),
            content_type="movie",
            title=details.get('title'),
            poster_path=details.get('poster_path'),
            overview=details.get('overview'),
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


