import requests

BASE_URL = "https://www.googleapis.com/books/v1/volumes"

# Book categories/subjects for filtering
BOOK_CATEGORIES = [
    {"id": "fiction", "name": "Kurgu"},
    {"id": "nonfiction", "name": "Kurgu Dışı"},
    {"id": "mystery", "name": "Gizem"},
    {"id": "romance", "name": "Romantik"},
    {"id": "science-fiction", "name": "Bilim Kurgu"},
    {"id": "fantasy", "name": "Fantastik"},
    {"id": "thriller", "name": "Gerilim"},
    {"id": "horror", "name": "Korku"},
    {"id": "biography", "name": "Biyografi"},
    {"id": "history", "name": "Tarih"},
    {"id": "science", "name": "Bilim"},
    {"id": "philosophy", "name": "Felsefe"},
    {"id": "psychology", "name": "Psikoloji"},
    {"id": "self-help", "name": "Kişisel Gelişim"},
    {"id": "poetry", "name": "Şiir"},
    {"id": "drama", "name": "Drama"},
    {"id": "children", "name": "Çocuk"},
    {"id": "young-adult", "name": "Genç Yetişkin"},
    {"id": "comics", "name": "Çizgi Roman"},
    {"id": "cooking", "name": "Yemek"},
]

def get_book_categories():
    """Return list of book categories for filtering"""
    return BOOK_CATEGORIES

def search_books(query: str):
    params = {
        "q": query,
        "langRestrict": "tr",
        "maxResults": 20
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_book_details(book_id: str):
    url = f"{BASE_URL}/{book_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_popular_books(page: int = 1):
    # Search for "best sellers" to get more popular results
    startIndex = (page - 1) * 20
    params = {
        "q": "subject:fiction",
        "langRestrict": "tr",
        "printType": "books",
        "maxResults": 20,
        "startIndex": startIndex
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return None


def discover_books(page: int = 1, category: str = None, year: int = None):
    """Discover books with filters"""
    startIndex = (page - 1) * 20
    
    # Build query
    query_parts = []
    
    if category:
        query_parts.append(f"subject:{category}")
    else:
        query_parts.append("subject:fiction")  # Default
    
    params = {
        "q": " ".join(query_parts),
        "printType": "books",
        "maxResults": 40,  # Get more to have room for filtering
        "startIndex": startIndex,
        "orderBy": "relevance"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        print(f"Google Books API Request: {response.url}")
        print(f"Google Books API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter by year if specified
            if year and 'items' in data:
                filtered_items = []
                for item in data.get('items', []):
                    volume_info = item.get('volumeInfo', {})
                    published_date = volume_info.get('publishedDate', '')
                    # Check if year matches (publishedDate can be "2018", "2018-05", "2018-05-15")
                    if published_date and published_date.startswith(str(year)):
                        filtered_items.append(item)
                
                if filtered_items:
                    data['items'] = filtered_items[:20]  # Limit to 20
                    data['totalItems'] = len(filtered_items)
                else:
                    # Yıl filtresiyle sonuç bulunamadıysa, yılsız sonuçları döndür
                    data['items'] = data.get('items', [])[:20]
            else:
                # Yıl filtresi yoksa sadece ilk 20'yi al
                data['items'] = data.get('items', [])[:20]
            
            return data
        print(f"Google Books API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Google Books Request Exception: {e}")
    
    # Return empty result instead of None
    return {"items": [], "totalItems": 0}
