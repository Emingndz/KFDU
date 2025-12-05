const API_URL = "http://127.0.0.1:8000/api/v1";

const api = {
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/login/access-token`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            let errorMessage = error.detail;
            if (Array.isArray(error.detail)) {
                errorMessage = error.detail.map(e => e.msg).join(', ');
            }
            throw new Error(errorMessage);
        }
        return response.json();
    },

    async register(email, username, password) {
        const response = await fetch(`${API_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            const error = await response.json();
            let errorMessage = error.detail;
            if (Array.isArray(error.detail)) {
                errorMessage = error.detail.map(e => `${e.loc[1]}: ${e.msg}`).join('\n');
            }
            throw new Error(errorMessage);
        }
        return response.json();
    },

    async getMe(token) {
        const response = await fetch(`${API_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Unauthorized');
        return response.json();
    },

    async searchMovies(query) {
        const response = await fetch(`${API_URL}/movies/search?query=${query}`);
        return response.json();
    },

    async searchBooks(query) {
        const response = await fetch(`${API_URL}/books/search?query=${query}`);
        return response.json();
    },

    async getPopularMovies(page = 1) {
        const response = await fetch(`${API_URL}/movies/popular?page=${page}`);
        if (!response.ok) {
            console.error('Popular movies error:', await response.text());
            throw new Error('Failed to fetch popular movies');
        }
        return response.json();
    },

    async getPopularBooks(page = 1) {
        const response = await fetch(`${API_URL}/books/popular?page=${page}`);
        if (!response.ok) {
            console.error('Popular books error:', await response.text());
            throw new Error('Failed to fetch popular books');
        }
        return response.json();
    },

    async interactWithMovie(token, externalId, rating, review, status) {
        const params = new URLSearchParams({ external_id: externalId });
        if (rating) params.append('rating', rating);
        if (review) params.append('review', review);
        if (status) params.append('status', status);

        const response = await fetch(`${API_URL}/movies/interact?${params.toString()}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Interaction failed');
        return response.json();
    },

    async interactWithBook(token, externalId, rating, review, status) {
        const params = new URLSearchParams({ external_id: externalId });
        if (rating) params.append('rating', rating);
        if (review) params.append('review', review);
        if (status) params.append('status', status);

        const response = await fetch(`${API_URL}/books/interact?${params.toString()}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Interaction failed');
        return response.json();
    },

    async getFeed(token) {
        const response = await fetch(`${API_URL}/feed/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.json();
    },

    async getUserInteractions(token) {
        const response = await fetch(`${API_URL}/users/me/interactions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch interactions');
        return response.json();
    },

    async searchUsers(query) {
        const response = await fetch(`${API_URL}/users/search?query=${query}`);
        if (!response.ok) throw new Error('Failed to search users');
        return response.json();
    },

    async followUser(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}/follow`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to follow user');
        return response.json();
    },

    async unfollowUser(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}/unfollow`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to unfollow user');
        return response.json();
    },

    async getMyFollowing(token) {
        const response = await fetch(`${API_URL}/users/me/following`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch following list');
        return response.json();
    },

    async getUserProfile(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch user profile');
        return response.json();
    },

    async getOtherUserInteractions(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}/interactions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch user interactions');
        return response.json();
    },

    async getOtherUserPlaylists(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}/playlists`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch user playlists');
        return response.json();
    },

    async updateProfile(token, bio, avatarUrl, email) {
        const body = { bio, avatar_url: avatarUrl };
        if (email) body.email = email;
        
        const response = await fetch(`${API_URL}/users/me`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Profil güncellenemedi');
        }
        return response.json();
    },

    async getMyFollowers(token) {
        const response = await fetch(`${API_URL}/users/me/followers`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch followers list');
        return response.json();
    },

    async getUserFollowing(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}/following`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch following list');
        return response.json();
    },

    async getUserFollowers(token, userId) {
        const response = await fetch(`${API_URL}/users/${userId}/followers`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch followers list');
        return response.json();
    },

    async getMyPlaylists(token) {
        const response = await fetch(`${API_URL}/playlists/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch playlists');
        return response.json();
    },

    async createPlaylist(token, title, description) {
        const response = await fetch(`${API_URL}/playlists/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, description })
        });
        if (!response.ok) throw new Error('Failed to create playlist');
        return response.json();
    },

    async getPlaylist(token, playlistId) {
        const response = await fetch(`${API_URL}/playlists/${playlistId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch playlist');
        return response.json();
    },

    async addToPlaylist(token, playlistId, externalId, contentType) {
        const params = new URLSearchParams({ 
            external_id: externalId,
            content_type: contentType
        });
        const response = await fetch(`${API_URL}/playlists/${playlistId}/items?${params.toString()}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to add to playlist');
        return response.json();
    },

    async removeFromPlaylist(token, playlistId, contentId) {
        const response = await fetch(`${API_URL}/playlists/${playlistId}/items/${contentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to remove from playlist');
        return response.json();
    },

    async requestPasswordReset(email) {
        const response = await fetch(`${API_URL}/password-reset/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Şifre sıfırlama isteği başarısız');
        }
        return response.json();
    },

    async verifyResetCode(code) {
        const response = await fetch(`${API_URL}/password-reset/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Kod doğrulanamadı');
        }
        return response.json();
    },

    async confirmPasswordReset(token, newPassword) {
        const response = await fetch(`${API_URL}/password-reset/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token, new_password: newPassword })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Şifre sıfırlama başarısız');
        }
        return response.json();
    },

    // Feed etkileşimleri - Beğeni
    async likeInteraction(token, interactionId) {
        const response = await fetch(`${API_URL}/feed/interactions/${interactionId}/like`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Beğeni eklenemedi');
        }
        return response.json();
    },

    async unlikeInteraction(token, interactionId) {
        const response = await fetch(`${API_URL}/feed/interactions/${interactionId}/like`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Beğeni kaldırılamadı');
        }
        return response.json();
    },

    // Feed etkileşimleri - Yorum
    async addComment(token, interactionId, text) {
        const response = await fetch(`${API_URL}/feed/interactions/${interactionId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ text })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Yorum eklenemedi');
        }
        return response.json();
    },

    async deleteComment(token, interactionId, commentId) {
        const response = await fetch(`${API_URL}/feed/interactions/${interactionId}/comments/${commentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Yorum silinemedi');
        }
        return response.json();
    },

    // Gelişmiş film filtreleme
    async getMovieGenres() {
        const response = await fetch(`${API_URL}/movies/genres`);
        if (!response.ok) throw new Error('Film türleri alınamadı');
        return response.json();
    },

    async discoverMovies(genreId = null, year = null, page = 1) {
        const params = new URLSearchParams({ page });
        if (genreId) params.append('genre', genreId);
        if (year) params.append('year', year);
        
        const response = await fetch(`${API_URL}/movies/discover?${params.toString()}`);
        if (!response.ok) throw new Error('Filmler keşfedilemedi');
        return response.json();
    },

    // Gelişmiş kitap filtreleme
    async getBookCategories() {
        const response = await fetch(`${API_URL}/books/categories`);
        if (!response.ok) throw new Error('Kitap kategorileri alınamadı');
        return response.json();
    },

    async discoverBooks(category = null, year = null, page = 1) {
        const params = new URLSearchParams({ page });
        if (category) params.append('category', category);
        if (year) params.append('year', year);
        
        const response = await fetch(`${API_URL}/books/discover?${params.toString()}`);
        if (!response.ok) throw new Error('Kitaplar keşfedilemedi');
        return response.json();
    },

    // İçerik istatistikleri ve yorumları
    async getMovieStats(externalId) {
        const response = await fetch(`${API_URL}/movies/${externalId}/platform-stats`);
        if (!response.ok) throw new Error('Film istatistikleri alınamadı');
        return response.json();
    },

    async getMovieReviews(externalId) {
        // Reviews are included in platform-stats, but we can call it separately too
        const response = await fetch(`${API_URL}/movies/${externalId}/platform-stats`);
        if (!response.ok) throw new Error('Film yorumları alınamadı');
        const data = await response.json();
        return data.reviews || [];
    },

    async getBookStats(externalId) {
        const response = await fetch(`${API_URL}/books/${externalId}/platform-stats`);
        if (!response.ok) throw new Error('Kitap istatistikleri alınamadı');
        return response.json();
    },

    async getBookReviews(externalId) {
        const response = await fetch(`${API_URL}/books/${externalId}/platform-stats`);
        if (!response.ok) throw new Error('Kitap yorumları alınamadı');
        const data = await response.json();
        return data.reviews || [];
    },

    // İçerik etkileşimlerini al (beğeni ve yorumlarla birlikte)
    async getContentInteractions(token, contentId) {
        const response = await fetch(`${API_URL}/feed/content/${contentId}/interactions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Etkileşimler alınamadı');
        return response.json();
    },

    async getInteractionDetails(token, interactionId) {
        const response = await fetch(`${API_URL}/feed/interactions/${interactionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Etkileşim detayları alınamadı');
        return response.json();
    }
};
