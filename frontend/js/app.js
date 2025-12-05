const { createApp, ref, onMounted, watch } = Vue;

createApp({
    setup() {
        const token = ref(localStorage.getItem('token'));
        const user = ref(null);
        const currentView = ref('login'); // login, register, feed, search
        const previousView = ref(null);
        
        // Login Form Data
        const loginForm = ref({ email: '', password: '' });
        const registerForm = ref({ email: '', username: '', password: '' });
        
        // Password Reset Data
        const forgotPasswordForm = ref({ email: '' });
        const resetPasswordForm = ref({ token: '', newPassword: '', confirmPassword: '' });
        const resetToken = ref('');
        
        // Search Data
        const searchQuery = ref('');
        const searchResults = ref([]);
        const searchType = ref('movie'); // movie or book

        // Feed Data
        const feedItems = ref([]);
        const userInteractions = ref([]);
        
        // Social Data
        const followedUsers = ref(new Set());
        const otherUser = ref(null);
        const otherUserInteractions = ref([]);
        const otherUserPlaylists = ref([]);
        let debounceTimeout = null;

        // User List Modal Data
        const showUserListModal = ref(false);
        const userListTitle = ref('');
        const userListUsers = ref([]);

        // Playlist Data
        const playlists = ref([]);
        const currentPlaylist = ref(null);
        const showCreatePlaylistModal = ref(false);
        const newPlaylistForm = ref({ title: '', description: '' });
        const showAddToPlaylistModal = ref(false);
        
        // Edit Profile Modal Data
        const showEditProfileModal = ref(false);
        const showAvatarSelectionModal = ref(false);
        const editProfileForm = ref({ bio: '', avatar_url: '', email: '' });
        
        // Feed Like/Comment Data
        const commentTexts = ref({});
        const showCommentsFor = ref(null);
        
        // Profile Tabs
        const profileActiveTab = ref('all');
        
        // Genre/Year Filter Data
        const movieGenres = ref([]);
        const bookCategories = ref([]);
        const selectedGenre = ref(null);
        const selectedCategory = ref(null);
        const selectedYear = ref(null);
        
        // Content Stats & Reviews
        const contentStats = ref(null);
        const contentReviews = ref([]);
        const contentInteractions = ref([]);
        
        const avatarOptions = [
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png', // Bulbasaur
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png', // Charmander
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png', // Squirtle
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png', // Pikachu
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/39.png', // Jigglypuff
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/52.png', // Meowth
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/54.png', // Psyduck
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png', // Eevee
            'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/143.png', // Snorlax
        ];

        // Pagination
        const page = ref(1);
        const hasMore = ref(true);

        const errorMsg = ref('');
        const loading = ref(true);
        const loadingMore = ref(false);

        // Detail View Data (replacing Modal)
        const selectedItem = ref(null);
        const interactionForm = ref({
            rating: null,
            status: '',
            review: ''
        });
        
        const hoverRating = ref(0);

        const translateStatus = (status, type) => {
            if (type === 'movie') {
                const map = {
                    'watched': 'İzledim',
                    'watching': 'İzliyorum',
                    'plan_to_watch': 'İzleyeceğim',
                    'dropped': 'Yarım Bıraktım'
                };
                return map[status] || status;
            } else {
                const map = {
                    'watched': 'Okudum',
                    'watching': 'Okuyorum',
                    'plan_to_watch': 'Okuyacağım',
                    'dropped': 'Yarım Bıraktım'
                };
                return map[status] || status;
            }
        };

        const getStatusOptions = () => {
            const type = searchType.value; // 'movie' or 'book'
            if (type === 'movie') {
                return [
                    { value: 'watched', text: 'İzledim' },
                    { value: 'watching', text: 'İzliyorum' },
                    { value: 'plan_to_watch', text: 'İzleyeceğim' },
                    { value: 'dropped', text: 'Yarım Bıraktım' }
                ];
            } else {
                return [
                    { value: 'watched', text: 'Okudum' },
                    { value: 'watching', text: 'Okuyorum' },
                    { value: 'plan_to_watch', text: 'Okuyacağım' },
                    { value: 'dropped', text: 'Yarım Bıraktım' }
                ];
            }
        };

        const getPlaylistsForContent = (contentId) => {
            const targetPlaylists = currentView.value === 'user-profile' ? otherUserPlaylists.value : playlists.value;
            return targetPlaylists.filter(p => p.items && p.items.some(i => i.id === contentId));
        };

        const handleStarHover = (n, event) => {
            const rect = event.target.getBoundingClientRect();
            const width = rect.width;
            const x = event.clientX - rect.left;
            if (x < width / 2) {
                hoverRating.value = n - 0.5;
            } else {
                hoverRating.value = n;
            }
        };

        const resetStarHover = () => {
            hoverRating.value = 0;
        };

        const setRating = (n, event) => {
            const rect = event.target.getBoundingClientRect();
            const width = rect.width;
            const x = event.clientX - rect.left;
            if (x < width / 2) {
                interactionForm.value.rating = n - 0.5;
            } else {
                interactionForm.value.rating = n;
            }
        };

        const getStarClass = (n) => {
            const val = hoverRating.value || interactionForm.value.rating || 0;
            if (val >= n) return 'fas fa-star text-warning';
            if (val >= n - 0.5) return 'fas fa-star-half-alt text-warning';
            return 'far fa-star text-muted';
        };

        const isItemInPlaylist = (playlist) => {
            if (!selectedItem.value || !playlist.items) return false;
            // Check both internal ID and external ID
            // selectedItem might be from search (has id as external_id) or from backend (has id as internal, external_id as external)
            
            const targetExternalId = selectedItem.value.external_id || String(selectedItem.value.id);
            
            return playlist.items.some(item => 
                item.external_id === targetExternalId
            );
        };

        const selectAvatar = (url) => {
            editProfileForm.value.avatar_url = url;
            showAvatarSelectionModal.value = false;
        };

        const checkAuth = async () => {
            if (token.value) {
                try {
                    user.value = await api.getMe(token.value);
                    await loadFollowedUsers();
                    currentView.value = 'feed';
                    loadFeed();
                } catch (e) {
                    console.error(e);
                    logout();
                }
            }
            loading.value = false;
        };

        const login = async () => {
            try {
                const data = await api.login(loginForm.value.email, loginForm.value.password);
                token.value = data.access_token;
                localStorage.setItem('token', data.access_token);
                errorMsg.value = ''; // Clear any previous error
                await checkAuth();
            } catch (e) {
                errorMsg.value = e.message;
            }
        };

        const register = async () => {
            try {
                await api.register(registerForm.value.email, registerForm.value.username, registerForm.value.password);
                // Auto login after register
                await api.login(registerForm.value.email, registerForm.value.password)
                    .then(data => {
                        token.value = data.access_token;
                        localStorage.setItem('token', data.access_token);
                        checkAuth();
                    });
            } catch (e) {
                errorMsg.value = e.message;
            }
        };

        const logout = () => {
            token.value = null;
            user.value = null;
            localStorage.removeItem('token');
            
            // Clear all state
            searchQuery.value = '';
            searchResults.value = [];
            feedItems.value = [];
            userInteractions.value = [];
            followedUsers.value = new Set();
            otherUser.value = null;
            otherUserInteractions.value = [];
            otherUserPlaylists.value = [];
            playlists.value = [];
            currentPlaylist.value = null;
            
            currentView.value = 'login';
        };

        // Password Reset Step Tracking
        const resetStep = ref(1); // 1: email, 2: code verification, 3: new password
        const resetCode = ref('');
        
        const requestPasswordReset = async () => {
            if (!forgotPasswordForm.value.email) {
                errorMsg.value = 'Lütfen e-posta adresinizi girin.';
                return;
            }
            try {
                const response = await api.requestPasswordReset(forgotPasswordForm.value.email);
                // E-postaya kod gönderildi, kod doğrulama adımına geç
                alert('Şifre sıfırlama kodu e-posta adresinize gönderildi! (Demo: ' + response.code + ')');
                resetStep.value = 2;
                currentView.value = 'reset-password';
            } catch (e) {
                errorMsg.value = e.message;
            }
        };
        
        const verifyResetCode = async () => {
            if (!resetCode.value) {
                errorMsg.value = 'Lütfen kodu girin.';
                return;
            }
            try {
                const response = await api.verifyResetCode(resetCode.value);
                if (response.valid) {
                    resetPasswordForm.value.token = response.token;
                    resetStep.value = 3;
                    alert('Kod doğrulandı! Yeni şifrenizi belirleyebilirsiniz.');
                }
            } catch (e) {
                errorMsg.value = e.message;
            }
        };

        const confirmPasswordReset = async () => {
            if (!resetPasswordForm.value.newPassword || !resetPasswordForm.value.confirmPassword) {
                errorMsg.value = 'Lütfen tüm alanları doldurun.';
                return;
            }
            if (resetPasswordForm.value.newPassword !== resetPasswordForm.value.confirmPassword) {
                errorMsg.value = 'Şifreler eşleşmiyor.';
                return;
            }
            if (resetPasswordForm.value.newPassword.length < 4) {
                errorMsg.value = 'Şifre en az 4 karakter olmalıdır.';
                return;
            }
            try {
                const response = await api.confirmPasswordReset(
                    resetPasswordForm.value.token,
                    resetPasswordForm.value.newPassword
                );
                alert(response.message);
                resetPasswordForm.value = { token: '', newPassword: '', confirmPassword: '' };
                resetToken.value = '';
                resetStep.value = 1;
                resetCode.value = '';
                forgotPasswordForm.value.email = '';
                currentView.value = 'login';
            } catch (e) {
                errorMsg.value = e.message;
            }
        };

        const handleSearch = async (resetPage = true) => {
            if (resetPage) {
                page.value = 1;
                searchResults.value = [];
                hasMore.value = true;
            }

            // If query is empty, load popular items
            if (!searchQuery.value) {
                loadPopularItems(resetPage);
                return;
            }
            
            if (searchType.value === 'movie') {
                const data = await api.searchMovies(searchQuery.value);
                console.log('Search Movies Data:', data);
                if (data && data.results) {
                    searchResults.value = data.results;
                    hasMore.value = false; // Search API usually doesn't support simple pagination like popular
                } else {
                    searchResults.value = [];
                }
            } else if (searchType.value === 'book') {
                const data = await api.searchBooks(searchQuery.value);
                console.log('Search Books Data:', data);
                if (data && data.items) {
                    searchResults.value = data.items;
                    hasMore.value = false;
                } else {
                    searchResults.value = [];
                }
            } else if (searchType.value === 'user') {
                const data = await api.searchUsers(searchQuery.value);
                console.log('Search Users Data:', data);
                searchResults.value = data || [];
                hasMore.value = false;
            }
        };

        const loadPopularItems = async (resetPage = true) => {
            if (loadingMore.value) return;
            loadingMore.value = true;

            try {
                if (resetPage) {
                    page.value = 1;
                    searchResults.value = [];
                }

                if (searchType.value === 'movie') {
                    const data = await api.getPopularMovies(page.value);
                    console.log('Popular Movies Data:', data);
                    if (data && data.results && data.results.length > 0) {
                        if (resetPage) {
                            searchResults.value = data.results;
                        } else {
                            searchResults.value = [...searchResults.value, ...data.results];
                        }
                    } else {
                        hasMore.value = false;
                    }
                } else if (searchType.value === 'book') {
                    const data = await api.getPopularBooks(page.value);
                    console.log('Popular Books Data:', data);
                    if (data && data.items && data.items.length > 0) {
                        if (resetPage) {
                            searchResults.value = data.items;
                        } else {
                            searchResults.value = [...searchResults.value, ...data.items];
                        }
                    } else {
                        hasMore.value = false;
                    }
                } else {
                    searchResults.value = [];
                }
            } finally {
                loadingMore.value = false;
            }
        };

        const loadMore = () => {
            page.value++;
            if (searchQuery.value) {
                // Search pagination not fully implemented for simplicity, just popular
            } else {
                loadPopularItems(false);
            }
        };

        const loadFollowedUsers = async () => {
             if (!token.value) return;
             try {
                 const users = await api.getMyFollowing(token.value);
                 followedUsers.value = new Set(users.map(u => u.id));
             } catch (e) {
                 console.error(e);
             }
        };

        const isFollowing = (userId) => {
            return followedUsers.value.has(userId);
        };

        const toggleFollow = async (targetUser) => {
            if (!token.value) return;
            try {
                if (isFollowing(targetUser.id)) {
                    await api.unfollowUser(token.value, targetUser.id);
                    followedUsers.value.delete(targetUser.id);
                } else {
                    await api.followUser(token.value, targetUser.id);
                    followedUsers.value.add(targetUser.id);
                }
                // Refresh user data to update counts if we are on profile or user-profile
                if (currentView.value === 'profile') {
                    user.value = await api.getMe(token.value);
                } else if (currentView.value === 'user-profile' && otherUser.value && otherUser.value.id === targetUser.id) {
                    otherUser.value = await api.getUserProfile(token.value, targetUser.id);
                    
                    // If we just followed, fetch their content immediately
                    if (isFollowing(targetUser.id)) {
                        otherUserInteractions.value = await api.getOtherUserInteractions(token.value, targetUser.id);
                        otherUserPlaylists.value = await api.getOtherUserPlaylists(token.value, targetUser.id);
                    } else {
                        // If unfollowed, clear content
                        otherUserInteractions.value = [];
                        otherUserPlaylists.value = [];
                    }
                }
                // Also refresh own user data in background to keep navbar/profile updated
                if (user.value) {
                     const me = await api.getMe(token.value);
                     user.value = me;
                }
            } catch (e) {
                alert('İşlem başarısız: ' + e.message);
            }
        };

        const viewUserProfile = async (userId) => {
            if (user.value && userId === user.value.id) {
                currentView.value = 'profile';
                return;
            }
            loading.value = true;
            try {
                otherUser.value = await api.getUserProfile(token.value, userId);
                
                // Try to fetch interactions and playlists. If not following, these might return empty or fail gracefully
                // But since we updated backend to return empty list if not following, we can just call them.
                // However, we should check if we are following to avoid unnecessary calls if we want, 
                // but backend handles security now.
                
                if (isFollowing(userId)) {
                    otherUserInteractions.value = await api.getOtherUserInteractions(token.value, userId);
                    otherUserPlaylists.value = await api.getOtherUserPlaylists(token.value, userId);
                } else {
                    otherUserInteractions.value = [];
                    otherUserPlaylists.value = [];
                }
                
                currentView.value = 'user-profile';
            } catch (e) {
                alert('Kullanıcı profili yüklenemedi: ' + e.message);
            } finally {
                loading.value = false;
            }
        };

        const openEditProfileModal = () => {
            if (!user.value) return;
            editProfileForm.value = {
                bio: user.value.bio || '',
                avatar_url: user.value.avatar_url || '',
                email: user.value.email || ''
            };
            showEditProfileModal.value = true;
        };

        const updateProfile = async () => {
            if (!user.value) return;
            try {
                const updatedUser = await api.updateProfile(
                    token.value, 
                    editProfileForm.value.bio, 
                    editProfileForm.value.avatar_url,
                    editProfileForm.value.email !== user.value.email ? editProfileForm.value.email : null
                );
                user.value = updatedUser;
                showEditProfileModal.value = false;
                alert("Profil güncellendi!");
            } catch (e) {
                alert("Güncelleme başarısız: " + e.message);
            }
        };

        const handleSearchInput = () => {
            if (debounceTimeout) clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                handleSearch();
            }, 500);
        };

        const openDetailView = (item) => {
            previousView.value = currentView.value;
            selectedItem.value = item;
            contentStats.value = null;
            contentReviews.value = [];
            
            // Determine content type
            if (item.content_type) {
                searchType.value = item.content_type;
            } else if (item.volumeInfo) {
                searchType.value = 'book';
            } else if (item.title && item.overview) { 
                // Fallback for movie search results which might not have content_type set explicitly in some API responses
                // But usually our backend or TMDB sets it. If coming from searchResults, we rely on searchType.
                // If coming from interaction list, it has content_type.
            }

            // Check for existing interaction
            const contentId = item.id; // This might be internal ID or external ID depending on source
            // We need to find if we have an interaction for this content.
            // Interactions in userInteractions have content.id (internal) and content.external_id
            
            // If item comes from search, it has 'id' as external_id (TMDB ID)
            // If item comes from backend (playlist/interaction), it has 'id' as internal ID and 'external_id'
            
            let existingInteraction = null;
            
            if (item.external_id) {
                // Item is from backend
                existingInteraction = userInteractions.value.find(i => i.content.id === item.id);
            } else {
                // Item is from search (external)
                existingInteraction = userInteractions.value.find(i => i.content.external_id === String(item.id) && i.content.content_type === searchType.value);
            }

            if (existingInteraction) {
                interactionForm.value = {
                    rating: existingInteraction.rating,
                    status: existingInteraction.status,
                    review: existingInteraction.review_text
                };
            } else {
                interactionForm.value = { rating: null, status: '', review: '' };
            }
            
            // Load content stats and reviews
            loadContentStats(item);
            
            // Load content interactions with likes/comments using external_id
            // If item comes from backend it has external_id, if from search item.id is the external_id
            const externalId = item.external_id || String(item.id);
            loadContentInteractions(externalId);
            
            currentView.value = 'detail';
        };

        const goBackFromDetail = () => {
            if (previousView.value) {
                currentView.value = previousView.value;
            } else {
                currentView.value = 'search';
            }
        };

        const saveInteraction = async () => {
            if (!selectedItem.value || !token.value) return;

            if (!interactionForm.value.rating && !interactionForm.value.status && !interactionForm.value.review) {
                alert("Lütfen puan, durum veya yorum alanlarından en az birini doldurun.");
                return;
            }

            try {
                const id = selectedItem.value.external_id || selectedItem.value.id;
                
                if (searchType.value === 'movie') {
                    await api.interactWithMovie(
                        token.value,
                        id,
                        interactionForm.value.rating,
                        interactionForm.value.review,
                        interactionForm.value.status
                    );
                } else {
                    await api.interactWithBook(
                        token.value,
                        id,
                        interactionForm.value.rating,
                        interactionForm.value.review,
                        interactionForm.value.status
                    );
                }
                
                alert('İşlem başarıyla kaydedildi!');
                
                // Reload user interactions
                await loadUserInteractions();
                
                // Reload content stats and interactions
                loadContentStats(selectedItem.value);
                const externalId = selectedItem.value.external_id || String(selectedItem.value.id);
                loadContentInteractions(externalId);
            } catch (e) {
                alert('Hata: ' + e.message);
            }
        };

        const openUserList = async (type, userId) => {
            if (!token.value) return;
            userListUsers.value = [];
            showUserListModal.value = true;
            try {
                if (type === 'followers') {
                    userListTitle.value = 'Takipçiler';
                    if (userId === user.value.id) {
                        userListUsers.value = await api.getMyFollowers(token.value);
                    } else {
                        userListUsers.value = await api.getUserFollowers(token.value, userId);
                    }
                } else {
                    userListTitle.value = 'Takip Edilenler';
                    if (userId === user.value.id) {
                        userListUsers.value = await api.getMyFollowing(token.value);
                    } else {
                        userListUsers.value = await api.getUserFollowing(token.value, userId);
                    }
                }
            } catch (e) {
                console.error(e);
                alert('Liste yüklenemedi.');
            }
        };

        const loadPlaylists = async () => {
            if (!token.value) return;
            try {
                playlists.value = await api.getMyPlaylists(token.value);
            } catch (e) {
                console.error(e);
            }
        };

        const createPlaylist = async () => {
            if (!token.value) return;
            try {
                await api.createPlaylist(token.value, newPlaylistForm.value.title, newPlaylistForm.value.description);
                newPlaylistForm.value = { title: '', description: '' };
                showCreatePlaylistModal.value = false;
                await loadPlaylists();
                alert('Liste oluşturuldu!');
            } catch (e) {
                alert('Hata: ' + e.message);
            }
        };

        const togglePlaylist = async (playlist) => {
            if (!selectedItem.value || !token.value) return;
            
            if (isItemInPlaylist(playlist)) {
                // Remove
                const targetExternalId = selectedItem.value.external_id || String(selectedItem.value.id);
                const itemInPlaylist = playlist.items.find(i => i.external_id === targetExternalId);
                
                if (!itemInPlaylist) {
                    alert("İçerik listede bulunamadı.");
                    return;
                }
                
                // if(!confirm('Bu içeriği listeden kaldırmak istediğinize emin misiniz?')) return;
                
                try {
                    await api.removeFromPlaylist(token.value, playlist.id, itemInPlaylist.id);
                    // Update local playlist state
                    const updatedPlaylist = await api.getPlaylist(token.value, playlist.id);
                    const index = playlists.value.findIndex(p => p.id === playlist.id);
                    if (index !== -1) {
                        playlists.value[index] = updatedPlaylist;
                    }
                    // alert('Listeden kaldırıldı!');
                } catch (e) {
                    alert('Hata: ' + e.message);
                }
            } else {
                // Add
                try {
                    const id = selectedItem.value.external_id || selectedItem.value.id;
                    const type = searchType.value === 'movie' ? 'movie' : 'book';
                    
                    await api.addToPlaylist(token.value, playlist.id, id, type);
                    
                    // Update local playlist state
                    const updatedPlaylist = await api.getPlaylist(token.value, playlist.id);
                    const index = playlists.value.findIndex(p => p.id === playlist.id);
                    if (index !== -1) {
                        playlists.value[index] = updatedPlaylist;
                    }
                    
                    // alert('Listeye eklendi!');
                } catch (e) {
                    alert('Hata: ' + e.message);
                }
            }
        };

        const viewPlaylist = async (playlist) => {
            if (!token.value) return;
            try {
                currentPlaylist.value = await api.getPlaylist(token.value, playlist.id);
                currentView.value = 'playlist-detail';
            } catch (e) {
                alert('Liste detayları yüklenemedi.');
            }
        };

        const removePlaylistContent = async (contentId) => {
             if (!token.value || !currentPlaylist.value) return;
             if(!confirm('Bu içeriği listeden kaldırmak istediğinize emin misiniz?')) return;
             try {
                 await api.removeFromPlaylist(token.value, currentPlaylist.value.id, contentId);
                 currentPlaylist.value = await api.getPlaylist(token.value, currentPlaylist.value.id);
             } catch (e) {
                 alert('Silinemedi: ' + e.message);
             }
        };

        // Watch for search type changes to reload popular items if query is empty
        watch(searchType, (newType) => {
            // Clear filters when changing type
            selectedGenre.value = null;
            selectedCategory.value = null;
            selectedYear.value = null;
            
            if (!searchQuery.value) {
                loadPopularItems();
            } else {
                handleSearch();
            }
            
            // Load appropriate filter options
            if (newType === 'movie' && movieGenres.value.length === 0) {
                loadGenres();
            } else if (newType === 'book' && bookCategories.value.length === 0) {
                loadBookCategories();
            }
        });

        // Watch for view changes to load data
        watch(currentView, (newView) => {
            if (newView === 'search' && searchResults.value.length === 0) {
                loadPopularItems();
                if (searchType.value === 'movie' && movieGenres.value.length === 0) {
                    loadGenres();
                } else if (searchType.value === 'book' && bookCategories.value.length === 0) {
                    loadBookCategories();
                }
            } else if (newView === 'profile') {
                loadUserInteractions();
                loadPlaylists();
            }
        });

        const loadFeed = async () => {
            if (!token.value) return;
            const data = await api.getFeed(token.value);
            feedItems.value = data;
        };

        // Feed Like/Unlike Functions
        const toggleLike = async (interaction) => {
            if (!token.value) return;
            try {
                if (interaction.user_liked) {
                    await api.unlikeInteraction(token.value, interaction.id);
                    interaction.user_liked = false;
                    interaction.likes_count = (interaction.likes_count || 1) - 1;
                } else {
                    await api.likeInteraction(token.value, interaction.id);
                    interaction.user_liked = true;
                    interaction.likes_count = (interaction.likes_count || 0) + 1;
                }
            } catch (e) {
                alert('Beğeni işlemi başarısız: ' + e.message);
            }
        };

        // Feed Comment Functions
        const toggleComments = (interactionId) => {
            if (showCommentsFor.value === interactionId) {
                showCommentsFor.value = null;
            } else {
                showCommentsFor.value = interactionId;
            }
        };

        const addComment = async (interaction) => {
            if (!token.value) return;
            const text = commentTexts.value[interaction.id];
            if (!text || !text.trim()) {
                alert('Yorum metni boş olamaz.');
                return;
            }
            try {
                const newComment = await api.addComment(token.value, interaction.id, text.trim());
                if (!interaction.comments) interaction.comments = [];
                interaction.comments.push(newComment);
                commentTexts.value[interaction.id] = '';
            } catch (e) {
                alert('Yorum eklenemedi: ' + e.message);
            }
        };

        const deleteComment = async (interaction, commentId) => {
            if (!token.value) return;
            if (!confirm('Bu yorumu silmek istediğinize emin misiniz?')) return;
            try {
                await api.deleteComment(token.value, interaction.id, commentId);
                interaction.comments = interaction.comments.filter(c => c.id !== commentId);
            } catch (e) {
                alert('Yorum silinemedi: ' + e.message);
            }
        };

        // Genre/Year Filter Functions
        const loadGenres = async () => {
            try {
                const data = await api.getMovieGenres();
                movieGenres.value = data.genres || [];
            } catch (e) {
                console.error('Türler yüklenemedi:', e);
            }
        };

        const loadBookCategories = async () => {
            try {
                console.log('Loading book categories...');
                const data = await api.getBookCategories();
                console.log('Book categories loaded:', data);
                bookCategories.value = data;
            } catch (e) {
                console.error('Kitap kategorileri yüklenemedi:', e);
            }
        };

        const applyFilters = async () => {
            console.log('Applying filters:', { type: searchType.value, category: selectedCategory.value, genre: selectedGenre.value, year: selectedYear.value });
            
            page.value = 1;
            searchResults.value = [];
            loadingMore.value = true;
            
            try {
                if (searchType.value === 'movie') {
                    const data = await api.discoverMovies(selectedGenre.value, selectedYear.value, 1);
                    console.log('Movie discover result:', data);
                    if (data && data.results) {
                        searchResults.value = data.results;
                        hasMore.value = data.results.length >= 20;
                    }
                } else if (searchType.value === 'book') {
                    const data = await api.discoverBooks(selectedCategory.value, selectedYear.value, 1);
                    console.log('Book discover result:', data);
                    if (data && data.items) {
                        searchResults.value = data.items;
                        hasMore.value = data.items.length >= 20;
                    } else if (data) {
                        // Boş sonuç
                        searchResults.value = [];
                        hasMore.value = false;
                    }
                }
            } catch (e) {
                console.error('İçerikler yüklenemedi:', e);
            } finally {
                loadingMore.value = false;
            }
        };

        const clearFilters = () => {
            selectedGenre.value = null;
            selectedCategory.value = null;
            selectedYear.value = null;
            if (!searchQuery.value) {
                loadPopularItems(true);
            }
        };

        // Content Stats & Reviews
        const loadContentStats = async (item) => {
            const externalId = item.external_id || item.id;
            try {
                if (searchType.value === 'movie') {
                    contentStats.value = await api.getMovieStats(externalId);
                    contentReviews.value = await api.getMovieReviews(externalId);
                } else {
                    contentStats.value = await api.getBookStats(externalId);
                    contentReviews.value = await api.getBookReviews(externalId);
                }
            } catch (e) {
                console.error('İstatistikler yüklenemedi:', e);
                contentStats.value = null;
                contentReviews.value = [];
            }
        };
        
        const loadContentInteractions = async (externalId) => {
            if (!token.value || !externalId) return;
            try {
                contentInteractions.value = await api.getContentInteractions(token.value, externalId);
            } catch (e) {
                console.error('İçerik etkileşimleri yüklenemedi:', e);
                contentInteractions.value = [];
            }
        };
        
        // Toggle like on content interaction (from detail page)
        const toggleInteractionLike = async (interaction) => {
            if (!token.value) return;
            try {
                if (interaction.user_liked) {
                    await api.unlikeInteraction(token.value, interaction.id);
                    interaction.user_liked = false;
                    interaction.likes_count = (interaction.likes_count || 1) - 1;
                } else {
                    await api.likeInteraction(token.value, interaction.id);
                    interaction.user_liked = true;
                    interaction.likes_count = (interaction.likes_count || 0) + 1;
                }
            } catch (e) {
                alert('Beğeni işlemi başarısız: ' + e.message);
            }
        };
        
        // Add comment on content interaction (from detail page)
        const addInteractionComment = async (interaction) => {
            if (!token.value) return;
            const text = commentTexts.value[interaction.id];
            if (!text || !text.trim()) {
                alert('Yorum metni boş olamaz.');
                return;
            }
            try {
                const newComment = await api.addComment(token.value, interaction.id, text.trim());
                if (!interaction.comments) interaction.comments = [];
                interaction.comments.push(newComment);
                commentTexts.value[interaction.id] = '';
            } catch (e) {
                alert('Yorum eklenemedi: ' + e.message);
            }
        };
        
        // Delete comment on content interaction (from detail page)  
        const deleteInteractionComment = async (interaction, commentId) => {
            if (!token.value) return;
            if (!confirm('Bu yorumu silmek istediğinize emin misiniz?')) return;
            try {
                await api.deleteComment(token.value, interaction.id, commentId);
                interaction.comments = interaction.comments.filter(c => c.id !== commentId);
            } catch (e) {
                alert('Yorum silinemedi: ' + e.message);
            }
        };
        
        // Toggle comments visibility for content interactions
        const toggleInteractionComments = (interactionId) => {
            if (showCommentsFor.value === interactionId) {
                showCommentsFor.value = null;
            } else {
                showCommentsFor.value = interactionId;
            }
        };

        // Profile Tab Filtering
        const getFilteredInteractions = () => {
            if (!userInteractions.value) return [];
            
            switch (profileActiveTab.value) {
                case 'watched_movies':
                    return userInteractions.value.filter(i => 
                        i.content.content_type === 'movie' && i.status === 'watched'
                    );
                case 'watching_movies':
                    return userInteractions.value.filter(i => 
                        i.content.content_type === 'movie' && i.status === 'watching'
                    );
                case 'plan_movies':
                    return userInteractions.value.filter(i => 
                        i.content.content_type === 'movie' && i.status === 'plan_to_watch'
                    );
                case 'watched_books':
                    return userInteractions.value.filter(i => 
                        i.content.content_type === 'book' && i.status === 'watched'
                    );
                case 'reading_books':
                    return userInteractions.value.filter(i => 
                        i.content.content_type === 'book' && i.status === 'watching'
                    );
                case 'plan_books':
                    return userInteractions.value.filter(i => 
                        i.content.content_type === 'book' && i.status === 'plan_to_watch'
                    );
                default:
                    return userInteractions.value;
            }
        };

        // Generate year options for filter
        const getYearOptions = () => {
            const currentYear = new Date().getFullYear();
            const years = [];
            for (let y = currentYear; y >= 1950; y--) {
                years.push(y);
            }
            return years;
        };

        const loadUserInteractions = async () => {
            if (!token.value) return;
            try {
                const data = await api.getUserInteractions(token.value);
                userInteractions.value = data;
            } catch (e) {
                console.error(e);
            }
        };

        onMounted(() => {
            checkAuth();
            // Load filter options
            loadGenres();
            loadBookCategories();
            
            window.addEventListener('scroll', () => {
                if (currentView.value === 'search' && hasMore.value && !loadingMore.value) {
                    // Increased threshold to 100px from bottom to prevent early triggering
                    // And added a check to ensure we have enough content to scroll
                    if (document.body.offsetHeight > window.innerHeight && 
                        (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
                        loadMore();
                    }
                }
            });
        });

        return {
            token,
            user,
            currentView,
            loginForm,
            registerForm,
            forgotPasswordForm,
            resetPasswordForm,
            resetToken,
            resetStep,
            resetCode,
            requestPasswordReset,
            verifyResetCode,
            confirmPasswordReset,
            searchQuery,
            searchResults,
            searchType,
            feedItems,
            userInteractions,
            errorMsg,
            login,
            register,
            logout,
            handleSearch,
            loading,
            loadingMore,
            saveInteraction,
            selectedItem,
            interactionForm,
            followedUsers,
            otherUser,
            otherUserInteractions,
            otherUserPlaylists,
            isFollowing,
            toggleFollow,
            viewUserProfile,
            openEditProfileModal,
            updateProfile,
            handleSearchInput,
            openDetailView,
            openUserList,
            showUserListModal,
            userListTitle,
            userListUsers,
            playlists,
            currentPlaylist,
            showCreatePlaylistModal,
            newPlaylistForm,
            showAddToPlaylistModal,
            showEditProfileModal,
            editProfileForm,
            loadMore,
            hasMore,
            createPlaylist,
            togglePlaylist,
            viewPlaylist,
            removePlaylistContent,
            goBackFromDetail,
            translateStatus,
            getStatusOptions,
            getPlaylistsForContent,
            hoverRating,
            handleStarHover,
            resetStarHover,
            setRating,
            getStarClass,
            isItemInPlaylist,
            avatarOptions,
            showAvatarSelectionModal,
            selectAvatar,
            // Feed Like/Comment
            toggleLike,
            toggleComments,
            addComment,
            deleteComment,
            commentTexts,
            showCommentsFor,
            // Profile Tabs
            profileActiveTab,
            getFilteredInteractions,
            // Filters
            movieGenres,
            bookCategories,
            selectedGenre,
            selectedCategory,
            selectedYear,
            applyFilters,
            clearFilters,
            getYearOptions,
            // Content Stats
            contentStats,
            contentReviews,
            contentInteractions,
            toggleInteractionLike,
            addInteractionComment,
            deleteInteractionComment,
            toggleInteractionComments
        };
    }
}).mount('#app');
