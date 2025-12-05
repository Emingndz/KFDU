import requests
from typing import Optional
from app.core.config import settings

BASE_URL = "https://api.themoviedb.org/3"

def search_movies(query: str):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": query,
        "language": "tr-TR"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"TMDb Search Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"TMDb Request Exception: {e}")
    return None

def get_movie_details(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "tr-TR",
        "append_to_response": "credits"  # Include cast and crew
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"TMDb Details Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"TMDb Request Exception: {e}")
    return None

def get_popular_movies(page: int = 1):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "tr-TR",
        "page": page
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"TMDb Popular Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"TMDb Request Exception: {e}")
    return None

def get_movie_genres():
    """Get list of movie genres"""
    url = f"{BASE_URL}/genre/movie/list"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "tr-TR"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"TMDb Genres Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"TMDb Request Exception: {e}")
    return {"genres": []}

def discover_movies(page: int = 1, genre: Optional[int] = None, year: Optional[int] = None, sort_by: str = "popularity.desc"):
    """Discover movies with filters"""
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "tr-TR",
        "page": page,
        "sort_by": sort_by
    }
    if genre:
        params["with_genres"] = genre
    if year:
        params["primary_release_year"] = year
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"TMDb Discover Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"TMDb Request Exception: {e}")
    return None
