// Global state
const state = {
    user: null,
    restaurants: [],
    categories: [],
    distances: [],
    selectedCategory: '',
    selectedDistance: 'nearby',  // Default to nearby
    currentResult: null,
    currentEntryId: null,
    history: [],
    cooldownTimer: null,
    cooldownEndTime: null,
    zipCode: '00000',  // Default zip code
    placesEnabled: false,  // Google Places feature enabled
    selectedPlace: null,  // Currently selected place from Google
    searchTimeout: null  // Debounce timeout for search
};

// DOM Elements
const elements = {
    welcomeModal: null,
    userRegistrationForm: null,
    firstNameInput: null,
    usernameDisplay: null,
    categoryButtonsContainer: null,
    distanceButtons: null,
    spinButton: null,
    resultDisplay: null,
    restaurantName: null,
    restaurantCategory: null,
    restaurantAddedBy: null,
    addRestaurantForm: null,
    restaurantNameInput: null,
    addCategoriesCheckboxes: null,
    restaurantDistanceInput: null,
    addClosedDaysCheckboxes: null,
    restaurantsList: null,
    restaurantCount: null,
    historyList: null,
    toast: null,
    goingButton: null,
    openAddModalBtn: null,
    addModal: null,
    closeAddModal: null,
    editModal: null,
    editRestaurantForm: null,
    editRestaurantId: null,
    editRestaurantName: null,
    editCategoriesCheckboxes: null,
    editRestaurantDistance: null,
    editClosedDaysCheckboxes: null,
    closeEditModal: null,
    deleteRestaurantBtn: null,
    newCategoryInput: null,
    addCategoryBtn: null,
    // Google Places elements (Add Modal)
    placesSearchGroup: null,
    restaurantSearchInput: null,
    placesAutocompleteResults: null,
    selectedPlaceInfo: null,
    clearSelectionBtn: null,
    placeIdInput: null,
    phoneInput: null,
    addressInput: null,
    websiteInput: null,
    googleDistanceInput: null,
    etaInput: null,
    // Google Places elements (Edit Modal)
    editPlacesSearchGroup: null,
    editRestaurantSearchInput: null,
    editPlacesAutocompleteResults: null,
    editPlaceIdInput: null,
    editPhoneInput: null,
    editAddressInput: null,
    editWebsiteInput: null,
    editGoogleDistanceInput: null,
    editEtaInput: null
};

// Initialize app on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    setupEventListeners();
    checkUser();
});

// Initialize DOM element references
function initializeElements() {
    elements.welcomeModal = document.getElementById('welcome-modal');
    elements.userRegistrationForm = document.getElementById('user-registration');
    elements.firstNameInput = document.getElementById('first-name');
    elements.usernameDisplay = document.getElementById('username');
    elements.categoryButtonsContainer = document.getElementById('category-buttons');
    elements.distanceButtons = document.querySelectorAll('.distance-btn');
    elements.spinButton = document.getElementById('spin-btn');
    elements.goingButton = document.getElementById('going-btn');
    elements.resultDisplay = document.getElementById('result-display');
    elements.restaurantName = document.getElementById('restaurant-name');
    elements.restaurantCategory = document.getElementById('restaurant-category');
    elements.restaurantAddedBy = document.getElementById('restaurant-added-by');
    elements.resultContactInfo = document.getElementById('result-contact-info');
    elements.addRestaurantForm = document.getElementById('add-restaurant-form');
    elements.restaurantNameInput = document.getElementById('restaurant-name-input');
    elements.addCategoriesCheckboxes = document.getElementById('add-categories-checkboxes');
    elements.restaurantDistanceInput = document.getElementById('restaurant-distance-input');
    elements.addClosedDaysCheckboxes = document.getElementById('add-closed-days-checkboxes');
    elements.restaurantsList = document.getElementById('restaurants-list');
    elements.restaurantCount = document.getElementById('restaurant-count');
    elements.historyList = document.getElementById('history-list');
    elements.toast = document.getElementById('toast');
    elements.openAddModalBtn = document.getElementById('open-add-modal');
    elements.addModal = document.getElementById('add-modal');
    elements.closeAddModal = document.getElementById('close-add-modal');
    elements.editModal = document.getElementById('edit-modal');
    elements.editRestaurantForm = document.getElementById('edit-restaurant-form');
    elements.editRestaurantId = document.getElementById('edit-restaurant-id');
    elements.editRestaurantName = document.getElementById('edit-restaurant-name');
    elements.editCategoriesCheckboxes = document.getElementById('edit-categories-checkboxes');
    elements.editRestaurantDistance = document.getElementById('edit-restaurant-distance');
    elements.editClosedDaysCheckboxes = document.getElementById('edit-closed-days-checkboxes');
    elements.closeEditModal = document.getElementById('close-edit-modal');
    elements.deleteRestaurantBtn = document.getElementById('delete-restaurant-btn');
    elements.newCategoryInput = document.getElementById('new-category-input');
    elements.addCategoryBtn = document.getElementById('add-category-btn');
    elements.statsBtn = document.getElementById('stats-btn');
    elements.statsModal = document.getElementById('stats-modal');
    elements.closeStatsModal = document.getElementById('close-stats-modal');
    elements.statsContent = document.getElementById('stats-content');
    elements.cooldownBanner = document.getElementById('cooldown-banner');
    elements.cooldownTime = document.getElementById('cooldown-time');
    // Google Places elements (Add Modal)
    elements.placesSearchGroup = document.getElementById('places-search-group');
    elements.restaurantSearchInput = document.getElementById('restaurant-search-input');
    elements.placesAutocompleteResults = document.getElementById('places-autocomplete-results');
    elements.selectedPlaceInfo = document.getElementById('selected-place-info');
    elements.clearSelectionBtn = document.getElementById('clear-selection-btn');
    elements.placeIdInput = document.getElementById('place-id-input');
    elements.phoneInput = document.getElementById('phone-input');
    elements.addressInput = document.getElementById('address-input');
    elements.websiteInput = document.getElementById('website-input');
    elements.googleDistanceInput = document.getElementById('google-distance-input');
    elements.etaInput = document.getElementById('eta-input');
    // Google Places elements (Edit Modal)
    elements.editPlacesSearchGroup = document.getElementById('edit-places-search-group');
    elements.editRestaurantSearchInput = document.getElementById('edit-restaurant-search-input');
    elements.editPlacesAutocompleteResults = document.getElementById('edit-places-autocomplete-results');
    elements.editPlaceIdInput = document.getElementById('edit-place-id-input');
    elements.editPhoneInput = document.getElementById('edit-phone-input');
    elements.editAddressInput = document.getElementById('edit-address-input');
    elements.editWebsiteInput = document.getElementById('edit-website-input');
    elements.editGoogleDistanceInput = document.getElementById('edit-google-distance-input');
    elements.editEtaInput = document.getElementById('edit-eta-input');
}

// Setup event listeners
function setupEventListeners() {
    // User registration
    elements.userRegistrationForm.addEventListener('submit', handleUserRegistration);

    // Distance filter buttons
    elements.distanceButtons.forEach(btn => {
        btn.addEventListener('click', () => handleDistanceChange(btn.dataset.distance));
    });

    // Spin button
    elements.spinButton.addEventListener('click', handleSpin);

    // Going button
    elements.goingButton.addEventListener('click', handleGoing);

    // Add restaurant form
    elements.addRestaurantForm.addEventListener('submit', handleAddRestaurant);

    // Add modal
    elements.openAddModalBtn.addEventListener('click', openAddModal);
    elements.closeAddModal.addEventListener('click', closeAddModal);

    // Edit modal
    elements.closeEditModal.addEventListener('click', closeEditModal);
    elements.editRestaurantForm.addEventListener('submit', handleEditRestaurant);
    elements.deleteRestaurantBtn.addEventListener('click', handleDeleteFromEdit);

    // Stats modal
    elements.statsBtn.addEventListener('click', openStatsModal);
    elements.closeStatsModal.addEventListener('click', closeStatsModal);

    // Custom category
    elements.addCategoryBtn.addEventListener('click', handleAddCategory);

    // Google Places search (Add Modal)
    if (elements.restaurantSearchInput) {
        elements.restaurantSearchInput.addEventListener('input', handleSearchInput);
    }
    if (elements.clearSelectionBtn) {
        elements.clearSelectionBtn.addEventListener('click', clearPlaceSelection);
    }

    // Google Places search (Edit Modal)
    if (elements.editRestaurantSearchInput) {
        elements.editRestaurantSearchInput.addEventListener('input', handleEditSearchInput);
    }

    // Close autocomplete when clicking outside
    document.addEventListener('click', (e) => {
        if (elements.placesAutocompleteResults &&
            !elements.placesAutocompleteResults.contains(e.target) &&
            e.target !== elements.restaurantSearchInput) {
            elements.placesAutocompleteResults.classList.add('hidden');
        }
        if (elements.editPlacesAutocompleteResults &&
            !elements.editPlacesAutocompleteResults.contains(e.target) &&
            e.target !== elements.editRestaurantSearchInput) {
            elements.editPlacesAutocompleteResults.classList.add('hidden');
        }
    });
}

// Check if user has a cookie
async function checkUser() {
    try {
        const response = await fetch('/api/user/check');
        const data = await response.json();

        if (data.exists && data.user) {
            state.user = data.user;
            elements.usernameDisplay.textContent = data.user;
            await loadConfig();
            await loadCategories();
            loadRestaurants();
            await loadHistory();
            checkCooldownStatus();
        } else {
            showWelcomeModal();
            await loadConfig();
            await loadCategories(); // Load categories even for new users
        }
    } catch (error) {
        console.error('Error checking user:', error);
        showWelcomeModal();
    }
}

// Load configuration from API
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();

        if (data.success) {
            state.zipCode = data.zip_code;
            state.placesEnabled = data.google_places_enabled || false;

            // Show/hide Google Places search based on enabled status
            if (state.placesEnabled && elements.placesSearchGroup) {
                elements.placesSearchGroup.classList.remove('hidden');
            } else if (elements.placesSearchGroup) {
                elements.placesSearchGroup.classList.add('hidden');
                // Make name input editable if Places is disabled
                if (elements.restaurantNameInput) {
                    elements.restaurantNameInput.removeAttribute('readonly');
                }
            }
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Show welcome modal for first-time users
function showWelcomeModal() {
    elements.welcomeModal.classList.remove('hidden');
    elements.firstNameInput.focus();
}

// Hide welcome modal
function hideWelcomeModal() {
    elements.welcomeModal.classList.add('hidden');
}

// Handle user registration
async function handleUserRegistration(e) {
    e.preventDefault();

    const firstName = elements.firstNameInput.value.trim();

    if (!firstName) {
        showToast('Please enter your first name', 'error');
        return;
    }

    try {
        const response = await fetch('/api/user/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ first_name: firstName })
        });

        const data = await response.json();

        if (data.success) {
            state.user = data.user;
            elements.usernameDisplay.textContent = data.user;
            hideWelcomeModal();
            showToast(data.message || `Welcome, ${data.user}!`, 'success');
            loadRestaurants();
            loadHistory();
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Error registering user:', error);
        showToast('Failed to register. Please try again.', 'error');
    }
}

// Load categories from API
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();

        if (data.success) {
            state.categories = data.categories;
            renderCategoryButtons();
            renderCategoryCheckboxes();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Render category filter buttons
function renderCategoryButtons() {
    const container = elements.categoryButtonsContainer;
    container.innerHTML = '';

    // Create "All" button
    const allBtn = document.createElement('button');
    allBtn.className = 'category-btn active';
    allBtn.dataset.category = '';
    allBtn.textContent = 'All';
    allBtn.addEventListener('click', () => handleCategoryChange(''));
    container.appendChild(allBtn);

    // Create category buttons
    state.categories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'category-btn';
        btn.dataset.category = category;
        btn.textContent = formatCategory(category);
        btn.addEventListener('click', () => handleCategoryChange(category));
        container.appendChild(btn);
    });
}

// Render category checkboxes for add form
function renderCategoryCheckboxes() {
    renderCheckboxesInContainer(elements.addCategoriesCheckboxes, state.categories);
    renderCheckboxesInContainer(elements.editCategoriesCheckboxes, state.categories);
}

// Helper to render checkboxes in a container
function renderCheckboxesInContainer(container, categories) {
    container.innerHTML = '';
    categories.forEach(category => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = category;
        checkbox.name = 'categories';

        const span = document.createElement('span');
        span.textContent = formatCategory(category);

        label.appendChild(checkbox);
        label.appendChild(span);
        container.appendChild(label);
    });
}

// Handle category change
function handleCategoryChange(category) {
    state.selectedCategory = category;

    // Update button states
    const buttons = elements.categoryButtonsContainer.querySelectorAll('.category-btn');
    buttons.forEach(btn => {
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Reload restaurants with filter
    loadRestaurants();
}

// Handle distance change
function handleDistanceChange(distance) {
    state.selectedDistance = distance;

    // Update button states
    elements.distanceButtons.forEach(btn => {
        if (btn.dataset.distance === distance) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Reload restaurants with filter
    loadRestaurants();
}

// Load restaurants from API
async function loadRestaurants() {
    try {
        const params = new URLSearchParams();
        if (state.selectedCategory) {
            params.append('category', state.selectedCategory);
        }
        if (state.selectedDistance) {
            params.append('distance', state.selectedDistance);
        }

        const url = params.toString()
            ? `/api/restaurants?${params.toString()}`
            : '/api/restaurants';

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            state.restaurants = data.restaurants;
            renderRestaurants();
        } else {
            showToast(data.error || 'Failed to load restaurants', 'error');
        }
    } catch (error) {
        console.error('Error loading restaurants:', error);
        showToast('Failed to load restaurants', 'error');
    }
}

// Render restaurants list
function renderRestaurants() {
    const list = elements.restaurantsList;
    const count = elements.restaurantCount;

    // Update count
    count.textContent = state.restaurants.length;

    // Clear list
    list.innerHTML = '';

    if (state.restaurants.length === 0) {
        list.innerHTML = '<p class="empty-message">No restaurants yet. Add one above!</p>';
        return;
    }

    // Create restaurant cards
    state.restaurants.forEach(restaurant => {
        const card = createRestaurantCard(restaurant);
        list.appendChild(card);
    });
}

// Create restaurant card element
function createRestaurantCard(restaurant) {
    const card = document.createElement('div');
    card.className = 'restaurant-card';
    card.onclick = () => openEditModal(restaurant);
    card.style.cursor = 'pointer';

    const info = document.createElement('div');
    info.className = 'restaurant-info';

    const nameContainer = document.createElement('div');
    nameContainer.className = 'restaurant-name-container';

    const name = document.createElement('h3');
    name.textContent = restaurant.name;

    const googleIcon = createGoogleIcon(restaurant.name);

    nameContainer.appendChild(name);
    nameContainer.appendChild(googleIcon);

    const meta = document.createElement('div');
    meta.className = 'restaurant-meta';

    // Show all categories
    const categories = Array.isArray(restaurant.categories) ? restaurant.categories : [restaurant.category || 'takeout'];
    categories.forEach(category => {
        const badge = document.createElement('span');
        badge.className = `category-badge ${category}`;
        badge.textContent = formatCategory(category);
        meta.appendChild(badge);
    });

    // Show distance
    const distanceBadge = document.createElement('span');
    distanceBadge.className = 'distance-badge';
    distanceBadge.textContent = formatDistance(restaurant.distance || 'nearby');
    meta.appendChild(distanceBadge);

    // const addedBy = document.createElement('span');
    // addedBy.textContent = `Added by ${restaurant.added_by}`;
    // meta.appendChild(addedBy);

    info.appendChild(nameContainer);
    info.appendChild(meta);

    // Add contact info if available from Google Places
    if (restaurant.phone || restaurant.website || restaurant.address || restaurant.google_distance) {
        const contactInfo = document.createElement('div');
        contactInfo.className = 'restaurant-contact';

        if (restaurant.phone) {
            const phoneLink = document.createElement('a');
            phoneLink.href = `tel:${restaurant.phone}`;
            phoneLink.className = 'contact-link';
            phoneLink.innerHTML = `📞 ${restaurant.phone}`;
            phoneLink.addEventListener('click', (e) => e.stopPropagation());
            contactInfo.appendChild(phoneLink);
        }

        if (restaurant.website) {
            const websiteLink = document.createElement('a');
            websiteLink.href = restaurant.website;
            websiteLink.target = '_blank';
            websiteLink.rel = 'noopener noreferrer';
            websiteLink.className = 'contact-link';
            websiteLink.innerHTML = `🌐 Website`;
            websiteLink.addEventListener('click', (e) => e.stopPropagation());
            contactInfo.appendChild(websiteLink);
        }

        if (restaurant.google_distance) {
            const distanceSpan = document.createElement('span');
            distanceSpan.className = 'contact-link';
            distanceSpan.style.cursor = 'default';
            const distanceText = formatMetersToMiles(restaurant.google_distance);
            const etaText = restaurant.eta ? ` (${formatETA(restaurant.eta)})` : '';
            distanceSpan.innerHTML = `📍 ${distanceText}${etaText}`;
            contactInfo.appendChild(distanceSpan);
        }

        if (restaurant.address) {
            const addressSpan = document.createElement('span');
            addressSpan.className = 'restaurant-address';
            addressSpan.textContent = restaurant.address;
            contactInfo.appendChild(addressSpan);
        }

        info.appendChild(contactInfo);
    }

    card.appendChild(info);

    return card;
}

// Format category for display
function formatCategory(category) {
    // Handle null/undefined
    if (!category) return 'Unknown';

    if (category === 'sit-down') return 'Sit Down';
    if (category === 'fast-food') return 'Fast Food';
    if (category === 'home') return 'Eat at Home';
    return category.charAt(0).toUpperCase() + category.slice(1);
}

// Format distance for display
function formatDistance(distance) {
    const map = {
        'nearby': 'Nearby',
        'short-drive': 'Short Drive',
        'medium-drive': 'Medium Drive',
        'far': 'Far'
    };
    return map[distance] || distance;
}

// Format meters to miles
function formatMetersToMiles(meters) {
    if (!meters) return 'Unknown';
    const miles = (meters * 0.000621371).toFixed(1);
    return `${miles} mi`;
}

// Format ETA minutes
function formatETA(minutes) {
    if (!minutes || minutes <= 0) return 'Unknown';
    if (minutes < 60) {
        return `~${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `~${hours}h ${mins}m` : `~${hours}h`;
}

// Convert meters to distance category
function metersToDistanceCategory(meters) {
    if (!meters) return 'nearby';

    const miles = meters * 0.000621371;

    if (miles <= 5) {
        return 'nearby';
    } else if (miles <= 10) {
        return 'short-drive';
    } else if (miles <= 20) {
        return 'medium-drive';
    } else {
        return 'far';
    }
}

// Debounced search input handler
function handleSearchInput(e) {
    const query = e.target.value.trim();

    // Clear previous timeout
    if (state.searchTimeout) {
        clearTimeout(state.searchTimeout);
    }

    // Hide results if query too short
    if (query.length < 2) {
        elements.placesAutocompleteResults.classList.add('hidden');
        return;
    }

    // Debounce: wait 300ms after user stops typing
    state.searchTimeout = setTimeout(() => {
        searchPlaces(query);
    }, 300);
}

// Search Google Places
async function searchPlaces(query) {
    try {
        const response = await fetch(`/api/places/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.places && data.places.length > 0) {
            renderPlaceResults(data.places);
        } else {
            elements.placesAutocompleteResults.innerHTML = '<p class="no-results">No results found</p>';
            elements.placesAutocompleteResults.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error searching places:', error);
        elements.placesAutocompleteResults.innerHTML = '<p class="no-results">Search failed. Please try again.</p>';
        elements.placesAutocompleteResults.classList.remove('hidden');
    }
}

// Render autocomplete results
function renderPlaceResults(places) {
    const container = elements.placesAutocompleteResults;
    container.innerHTML = '';

    places.forEach(place => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';

        const nameDiv = document.createElement('div');
        nameDiv.className = 'place-name';
        nameDiv.textContent = place.name;

        const addressDiv = document.createElement('div');
        addressDiv.className = 'place-address';
        addressDiv.textContent = place.address || 'Address not available';

        item.appendChild(nameDiv);
        item.appendChild(addressDiv);

        if (place.distance) {
            const distanceDiv = document.createElement('div');
            distanceDiv.className = 'place-distance';
            distanceDiv.textContent = formatMetersToMiles(place.distance);
            item.appendChild(distanceDiv);
        }

        item.addEventListener('click', (e) => {
            e.stopPropagation();
            // Hide dropdown immediately
            elements.placesAutocompleteResults.classList.add('hidden');
            selectPlace(place.place_id);
        });
        container.appendChild(item);
    });

    container.classList.remove('hidden');
}

// Select a place and fetch full details
async function selectPlace(placeId) {
    try {
        const response = await fetch(`/api/places/details/${placeId}`);
        const data = await response.json();

        if (data.success && data.place) {
            populateFormWithPlace(data.place);
            state.selectedPlace = data.place;
        } else {
            showToast('Failed to load place details', 'error');
        }
    } catch (error) {
        console.error('Error fetching place details:', error);
        showToast('Failed to load place details', 'error');
    }
}

// Populate form with place details
function populateFormWithPlace(place) {
    // Fill name
    elements.restaurantNameInput.value = place.name;
    elements.restaurantNameInput.setAttribute('readonly', true);

    // Fill hidden fields
    elements.placeIdInput.value = place.place_id || '';
    elements.phoneInput.value = place.phone || '';
    elements.addressInput.value = place.address || '';
    elements.websiteInput.value = place.website || '';
    elements.googleDistanceInput.value = place.distance || '';
    elements.etaInput.value = place.eta || '';

    // Auto-set distance dropdown based on Google distance
    if (place.distance) {
        const distanceCategory = metersToDistanceCategory(place.distance);
        elements.restaurantDistanceInput.value = distanceCategory;
    }

    // Show place info
    document.getElementById('selected-address').textContent = place.address || 'N/A';
    document.getElementById('selected-phone').textContent = place.phone || 'N/A';

    const websiteLink = document.getElementById('selected-website');
    if (place.website) {
        websiteLink.href = place.website;
        websiteLink.textContent = place.website;
        websiteLink.style.display = '';
    } else {
        websiteLink.textContent = 'N/A';
        websiteLink.removeAttribute('href');
    }

    document.getElementById('selected-distance').textContent = formatMetersToMiles(place.distance);
    document.getElementById('selected-eta').textContent = formatETA(place.eta);

    elements.selectedPlaceInfo.classList.remove('hidden');
    elements.placesAutocompleteResults.classList.add('hidden');
    elements.restaurantSearchInput.value = '';
}

// Clear selection and allow manual entry
function clearPlaceSelection() {
    state.selectedPlace = null;
    elements.restaurantNameInput.value = '';
    elements.restaurantNameInput.removeAttribute('readonly');
    elements.restaurantSearchInput.value = '';

    // Clear hidden fields
    elements.placeIdInput.value = '';
    elements.phoneInput.value = '';
    elements.addressInput.value = '';
    elements.websiteInput.value = '';
    elements.googleDistanceInput.value = '';
    elements.etaInput.value = '';

    // Hide place info
    elements.selectedPlaceInfo.classList.add('hidden');
}

// === Edit Modal Google Places Functions ===

// Debounced search input handler for edit modal
function handleEditSearchInput(e) {
    const query = e.target.value.trim();

    // Clear previous timeout
    if (state.searchTimeout) {
        clearTimeout(state.searchTimeout);
    }

    // Hide results if query too short
    if (query.length < 2) {
        elements.editPlacesAutocompleteResults.classList.add('hidden');
        return;
    }

    // Debounce: wait 300ms after user stops typing
    state.searchTimeout = setTimeout(() => {
        searchEditPlaces(query);
    }, 300);
}

// Search Google Places for edit modal
async function searchEditPlaces(query) {
    try {
        const response = await fetch(`/api/places/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.places && data.places.length > 0) {
            renderEditPlaceResults(data.places);
        } else {
            elements.editPlacesAutocompleteResults.innerHTML = '<p class="no-results">No results found</p>';
            elements.editPlacesAutocompleteResults.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error searching places:', error);
        elements.editPlacesAutocompleteResults.innerHTML = '<p class="no-results">Search failed. Please try again.</p>';
        elements.editPlacesAutocompleteResults.classList.remove('hidden');
    }
}

// Render autocomplete results for edit modal
function renderEditPlaceResults(places) {
    const container = elements.editPlacesAutocompleteResults;
    container.innerHTML = '';

    places.forEach(place => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';

        const nameDiv = document.createElement('div');
        nameDiv.className = 'place-name';
        nameDiv.textContent = place.name;

        const addressDiv = document.createElement('div');
        addressDiv.className = 'place-address';
        addressDiv.textContent = place.address || 'Address not available';

        item.appendChild(nameDiv);
        item.appendChild(addressDiv);

        if (place.distance) {
            const distanceDiv = document.createElement('div');
            distanceDiv.className = 'place-distance';
            distanceDiv.textContent = formatMetersToMiles(place.distance);
            item.appendChild(distanceDiv);
        }

        item.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            // Hide dropdown and clear search immediately
            elements.editPlacesAutocompleteResults.classList.add('hidden');
            elements.editRestaurantSearchInput.value = '';
            elements.editRestaurantSearchInput.blur(); // Remove focus
            selectEditPlace(place.place_id);
        });
        container.appendChild(item);
    });

    container.classList.remove('hidden');
}

// Select a place for edit modal and fetch full details
async function selectEditPlace(placeId) {
    try {
        const response = await fetch(`/api/places/details/${placeId}`);
        const data = await response.json();

        if (data.success && data.place) {
            populateEditFormWithPlace(data.place);
        } else {
            showToast('Failed to load place details', 'error');
        }
    } catch (error) {
        console.error('Error fetching place details:', error);
        showToast('Failed to load place details', 'error');
    }
}

// Populate edit form with place details
function populateEditFormWithPlace(place) {
    // Update name to match Google Places
    if (place.name) {
        elements.editRestaurantName.value = place.name;
    }

    // Fill hidden fields
    elements.editPlaceIdInput.value = place.place_id || '';
    elements.editPhoneInput.value = place.phone || '';
    elements.editAddressInput.value = place.address || '';
    elements.editWebsiteInput.value = place.website || '';
    elements.editGoogleDistanceInput.value = place.distance || '';
    elements.editEtaInput.value = place.eta || '';

    // Auto-set distance dropdown based on Google distance
    if (place.distance) {
        const distanceCategory = metersToDistanceCategory(place.distance);
        elements.editRestaurantDistance.value = distanceCategory;
    }

    // Update display
    const phoneLink = document.getElementById('edit-phone-link');
    if (place.phone) {
        phoneLink.href = `tel:${place.phone}`;
        phoneLink.textContent = place.phone;
    } else {
        phoneLink.textContent = 'N/A';
        phoneLink.removeAttribute('href');
    }

    document.getElementById('edit-address').textContent = place.address || 'N/A';

    const websiteLink = document.getElementById('edit-website-link');
    if (place.website) {
        websiteLink.href = place.website;
        websiteLink.textContent = place.website;
    } else {
        websiteLink.textContent = 'N/A';
        websiteLink.removeAttribute('href');
    }

    document.getElementById('edit-google-distance').textContent = formatMetersToMiles(place.distance);
    document.getElementById('edit-eta').textContent = formatETA(place.eta);

    // Show the info section
    document.getElementById('edit-place-info').classList.remove('hidden');
    elements.editPlacesAutocompleteResults.classList.add('hidden');
    elements.editRestaurantSearchInput.value = '';

    showToast('Google Places data updated! Click "Save Changes" to apply.', 'success');
}

// Create Google search URL for a restaurant
function createGoogleSearchUrl(restaurantName) {
    const query = encodeURIComponent(`${restaurantName} ${state.zipCode}`);
    return `https://www.google.com/search?q=${query}`;
}

// Create Google icon element
function createGoogleIcon(restaurantName) {
    const icon = document.createElement('a');
    icon.href = createGoogleSearchUrl(restaurantName);
    icon.target = '_blank';
    icon.rel = 'noopener noreferrer';
    icon.className = 'google-search-icon';
    icon.title = `Search Google for ${restaurantName}`;
    icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20" height="20">
        <path fill="#4285F4" d="M24 9.5c3.9 0 6.6 1.7 8.1 3.1l6-6C34.7 3.5 29.8 1 24 1 14.7 1 6.9 6.8 3.9 14.9l7.1 5.5C12.7 14.5 17.9 9.5 24 9.5z"/>
        <path fill="#34A853" d="M46.5 24c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.4 5.7C43.8 37.2 46.5 31.1 46.5 24z"/>
        <path fill="#FBBC05" d="M11 28.4c-.6-1.8-.9-3.7-.9-5.7s.3-3.9.9-5.7L3.9 11.5C2.1 15 1 18.9 1 23s1.1 8 2.9 11.5L11 28.4z"/>
        <path fill="#EA4335" d="M24 47c5.8 0 10.7-1.9 14.3-5.2l-7.4-5.7c-1.9 1.3-4.4 2.1-6.9 2.1-6.1 0-11.3-4.1-13.1-9.6l-7.1 5.5C6.9 41.2 14.7 47 24 47z"/>
    </svg>`;

    // Prevent click from bubbling to parent
    icon.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    return icon;
}

// Handle spin button
async function handleSpin() {
    if (state.restaurants.length === 0) {
        showToast('No restaurants available. Add some first!', 'error');
        return;
    }

    // Add spinning animation
    elements.spinButton.classList.add('spinning');

    try {
        const params = new URLSearchParams();
        if (state.selectedCategory) {
            params.append('category', state.selectedCategory);
        }
        if (state.selectedDistance) {
            params.append('distance', state.selectedDistance);
        }

        const url = params.toString()
            ? `/api/randomize?${params.toString()}`
            : '/api/randomize';

        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.restaurant) {
            state.currentResult = data.restaurant;
            state.currentEntryId = data.entry_id;
            showResult(data.restaurant);
            loadHistory(); // Reload history to show the new spin
        } else {
            // Handle rate limiting (429) specially
            if (response.status === 429 && data.seconds_remaining) {
                showCooldownBanner(data.seconds_remaining);
            } else {
                showToast(data.error || 'No restaurants available', 'error');
            }
        }
    } catch (error) {
        console.error('Error getting random restaurant:', error);
        showToast('Failed to pick a restaurant', 'error');
    } finally {
        // Remove spinning animation after delay
        setTimeout(() => {
            elements.spinButton.classList.remove('spinning');
        }, 500);
    }
}

// Show result
function showResult(restaurant) {
    // Clear and rebuild the restaurant name with Google icon
    elements.restaurantName.innerHTML = '';

    const nameText = document.createTextNode(restaurant.name);
    elements.restaurantName.appendChild(nameText);

    const googleIcon = createGoogleIcon(restaurant.name);
    googleIcon.style.marginLeft = '10px';
    elements.restaurantName.appendChild(googleIcon);

    // Clear and populate contact info
    elements.resultContactInfo.innerHTML = '';

    if (restaurant.phone || restaurant.website || restaurant.address || restaurant.google_distance) {
        if (restaurant.phone) {
            const phoneLink = document.createElement('a');
            phoneLink.href = `tel:${restaurant.phone}`;
            phoneLink.className = 'contact-link';
            phoneLink.innerHTML = `📞 ${restaurant.phone}`;
            elements.resultContactInfo.appendChild(phoneLink);
        }

        if (restaurant.website) {
            const websiteLink = document.createElement('a');
            websiteLink.href = restaurant.website;
            websiteLink.target = '_blank';
            websiteLink.rel = 'noopener noreferrer';
            websiteLink.className = 'contact-link';
            websiteLink.innerHTML = `🌐 Website`;
            elements.resultContactInfo.appendChild(websiteLink);
        }

        if (restaurant.google_distance) {
            const distanceSpan = document.createElement('span');
            distanceSpan.className = 'contact-link';
            distanceSpan.style.cursor = 'default';
            const distanceText = formatMetersToMiles(restaurant.google_distance);
            const etaText = restaurant.eta ? ` (${formatETA(restaurant.eta)})` : '';
            distanceSpan.innerHTML = `📍 ${distanceText}${etaText}`;
            elements.resultContactInfo.appendChild(distanceSpan);
        }

        if (restaurant.address) {
            const addressSpan = document.createElement('span');
            addressSpan.className = 'restaurant-address';
            addressSpan.textContent = restaurant.address;
            elements.resultContactInfo.appendChild(addressSpan);
        }
    }

    elements.resultDisplay.classList.remove('hidden');

    // Reset going button
    elements.goingButton.classList.remove('marked');
    elements.goingButton.textContent = "✓ We're Going!";

    // Scroll to result
    elements.resultDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Handle going button
async function handleGoing() {
    if (!state.currentEntryId) {
        showToast('No current spin to mark', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/history/${state.currentEntryId}/went`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || "Marked as went!", 'success');
            elements.goingButton.classList.add('marked');
            elements.goingButton.textContent = "✓ Marked!";
            loadHistory(); // Reload history to show the went badge
        } else {
            showToast(data.error || 'Failed to mark as went', 'error');
        }
    } catch (error) {
        console.error('Error marking as went:', error);
        showToast('Failed to mark as went', 'error');
    }
}

// Handle add restaurant
async function handleAddRestaurant(e) {
    e.preventDefault();

    const name = elements.restaurantNameInput.value.trim();
    const distance = elements.restaurantDistanceInput.value;

    // Get selected categories from checkboxes
    const categoryCheckboxes = elements.addCategoriesCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
    const categories = Array.from(categoryCheckboxes).map(cb => cb.value);

    // Get selected closed days from checkboxes
    const closedDaysCheckboxes = elements.addClosedDaysCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
    const closedDays = Array.from(closedDaysCheckboxes).map(cb => parseInt(cb.value));

    // Get Google Places data from hidden fields
    const placeId = elements.placeIdInput.value || '';
    const phone = elements.phoneInput.value || '';
    const address = elements.addressInput.value || '';
    const website = elements.websiteInput.value || '';
    const googleDistance = elements.googleDistanceInput.value || '';
    const eta = elements.etaInput.value || '';

    if (!name) {
        showToast('Please enter a restaurant name', 'error');
        return;
    }

    if (categories.length === 0) {
        showToast('Please select at least one category', 'error');
        return;
    }

    try {
        const response = await fetch('/api/restaurants', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                categories,
                distance,
                closed_days: closedDays,
                // Google Places data
                place_id: placeId,
                phone: phone,
                address: address,
                website: website,
                google_distance: googleDistance,
                eta: eta
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || 'Restaurant added!', 'success');
            elements.addRestaurantForm.reset();
            clearPlaceSelection();  // Clear Google Places selection
            closeAddModal();
            loadRestaurants();
        } else {
            showToast(data.error || 'Failed to add restaurant', 'error');
        }
    } catch (error) {
        console.error('Error adding restaurant:', error);
        showToast('Failed to add restaurant', 'error');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast ${type}`;
    elements.toast.classList.remove('hidden');

    // Auto-hide after 3 seconds
    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 3000);
}

// Check if there's an active cooldown
async function checkCooldownStatus() {
    if (!state.user) return;

    try {
        // Make a test randomize request to check cooldown
        const params = new URLSearchParams();
        const url = `/api/randomize?${params.toString()}`;

        const response = await fetch(url);
        const data = await response.json();

        // If we get a 429, there's an active cooldown
        if (response.status === 429 && data.seconds_remaining) {
            showCooldownBanner(data.seconds_remaining);
        }
    } catch (error) {
        console.error('Error checking cooldown status:', error);
    }
}

// Load spin history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        if (data.success) {
            state.history = data.history;
            renderHistory();
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Render history list
function renderHistory() {
    const list = elements.historyList;

    // Clear list
    list.innerHTML = '';

    if (state.history.length === 0) {
        list.innerHTML = '<p class="empty-message">No spins yet. Try the wheel above!</p>';
        return;
    }

    // Create history items
    state.history.forEach(entry => {
        const item = createHistoryItem(entry);
        list.appendChild(item);
    });
}

// Create history item element
function createHistoryItem(entry) {
    const item = document.createElement('div');
    item.className = entry.went ? 'history-item went' : 'history-item';

    const header = document.createElement('div');
    header.className = 'history-header';

    const restaurantName = document.createElement('span');
    restaurantName.className = 'history-restaurant';
    restaurantName.textContent = entry.restaurant_name;

    const time = document.createElement('span');
    time.className = 'history-time';
    time.textContent = formatTimeAgo(entry.timestamp);

    header.appendChild(restaurantName);
    header.appendChild(time);

    const meta = document.createElement('div');
    meta.className = 'history-meta';

    const badge = document.createElement('span');
    badge.className = `category-badge ${entry.category}`;
    badge.textContent = formatCategory(entry.category);

    const spinner = document.createElement('span');
    spinner.textContent = `Spun by ${entry.username}`;

    meta.appendChild(badge);
    meta.appendChild(spinner);

    // Add "went" badge if applicable
    if (entry.went) {
        const wentBadge = document.createElement('span');
        wentBadge.className = 'went-badge';
        wentBadge.textContent = '✓ Went';
        meta.appendChild(wentBadge);
    }

    item.appendChild(header);
    item.appendChild(meta);

    return item;
}

// Show cooldown banner with countdown
async function showCooldownBanner(secondsRemaining) {
    // Clear any existing timer
    if (state.cooldownTimer) {
        clearInterval(state.cooldownTimer);
    }

    // Set end time
    state.cooldownEndTime = Date.now() + (secondsRemaining * 1000);

    // Show banner
    elements.cooldownBanner.classList.remove('hidden');

    // Disable spin button
    elements.spinButton.disabled = true;
    elements.spinButton.style.opacity = '0.5';
    elements.spinButton.style.cursor = 'not-allowed';

    // Update countdown immediately
    updateCooldownDisplay();

    // Start countdown timer
    state.cooldownTimer = setInterval(() => {
        updateCooldownDisplay();
    }, 1000);

    // Show the last spin result if available
    if (!state.currentResult && state.history && state.history.length > 0) {
        // Get the most recent spin from history
        const lastSpin = state.history[0];

        // Fetch the full restaurant details to display
        try {
            const response = await fetch('/api/restaurants');
            const data = await response.json();

            if (data.success) {
                const restaurant = data.restaurants.find(r => r.name === lastSpin.restaurant_name);
                if (restaurant) {
                    state.currentResult = restaurant;
                    state.currentEntryId = lastSpin.id;
                    showResult(restaurant);
                }
            }
        } catch (error) {
            console.error('Error loading last spin:', error);
        }
    }
}

// Update cooldown display
function updateCooldownDisplay() {
    const now = Date.now();
    const remaining = Math.max(0, Math.floor((state.cooldownEndTime - now) / 1000));

    if (remaining <= 0) {
        hideCooldownBanner();
        return;
    }

    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;

    let timeText;
    if (minutes > 0) {
        timeText = seconds > 0 ? `${minutes}m ${seconds}s` : `${minutes}m`;
    } else {
        timeText = `${seconds}s`;
    }

    elements.cooldownTime.textContent = timeText;
}

// Hide cooldown banner
function hideCooldownBanner() {
    if (state.cooldownTimer) {
        clearInterval(state.cooldownTimer);
        state.cooldownTimer = null;
    }

    elements.cooldownBanner.classList.add('hidden');

    // Re-enable spin button
    elements.spinButton.disabled = false;
    elements.spinButton.style.opacity = '1';
    elements.spinButton.style.cursor = 'pointer';
}

// Format timestamp to relative time
function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Unknown';

    const now = new Date();
    // Ensure the timestamp is parsed correctly (add 'Z' if not present to indicate UTC)
    const timestampStr = timestamp.endsWith('Z') ? timestamp : timestamp + 'Z';
    const then = new Date(timestampStr);
    const seconds = Math.floor((now - then) / 1000);

    // Handle invalid dates or future dates
    if (isNaN(then.getTime()) || seconds < 0) {
        return 'Just now';
    }

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

    return then.toLocaleDateString();
}

// Open add modal
function openAddModal() {
    elements.addModal.classList.remove('hidden');
}

// Close add modal
function closeAddModal() {
    elements.addModal.classList.add('hidden');
    elements.addRestaurantForm.reset();
}

// Open edit modal with restaurant data
function openEditModal(restaurant) {
    // Clear search input and autocomplete from any previous edits
    if (elements.editRestaurantSearchInput) {
        elements.editRestaurantSearchInput.value = '';
    }
    if (elements.editPlacesAutocompleteResults) {
        elements.editPlacesAutocompleteResults.classList.add('hidden');
        elements.editPlacesAutocompleteResults.innerHTML = '';
    }

    // Clear all Google Places display elements from any previous searches
    const editPlaceInfo = document.getElementById('edit-place-info');
    if (editPlaceInfo) {
        editPlaceInfo.classList.add('hidden');
    }
    const phoneLink = document.getElementById('edit-phone-link');
    if (phoneLink) {
        phoneLink.textContent = '';
        phoneLink.removeAttribute('href');
    }
    const websiteLink = document.getElementById('edit-website-link');
    if (websiteLink) {
        websiteLink.textContent = '';
        websiteLink.removeAttribute('href');
    }
    document.getElementById('edit-address').textContent = '';
    document.getElementById('edit-google-distance').textContent = '';
    document.getElementById('edit-eta').textContent = '';

    elements.editRestaurantId.value = restaurant.id;
    elements.editRestaurantName.value = restaurant.name;
    elements.editRestaurantDistance.value = restaurant.distance || 'nearby';

    // Check the appropriate category checkboxes
    const categories = Array.isArray(restaurant.categories) ? restaurant.categories : [restaurant.category || 'takeout'];
    const categoryCheckboxes = elements.editCategoriesCheckboxes.querySelectorAll('input[type="checkbox"]');
    categoryCheckboxes.forEach(cb => {
        cb.checked = categories.includes(cb.value);
    });

    // Check the appropriate closed days checkboxes
    const closedDays = restaurant.closed_days || [];
    const closedDaysCheckboxes = elements.editClosedDaysCheckboxes.querySelectorAll('input[type="checkbox"]');
    closedDaysCheckboxes.forEach(cb => {
        cb.checked = closedDays.includes(parseInt(cb.value));
    });

    // Show/hide Google Places search group
    if (state.placesEnabled && elements.editPlacesSearchGroup) {
        elements.editPlacesSearchGroup.classList.remove('hidden');
    }

    // Populate hidden fields with current Google Places data
    elements.editPlaceIdInput.value = restaurant.place_id || '';
    elements.editPhoneInput.value = restaurant.phone || '';
    elements.editAddressInput.value = restaurant.address || '';
    elements.editWebsiteInput.value = restaurant.website || '';
    elements.editGoogleDistanceInput.value = restaurant.google_distance || '';
    elements.editEtaInput.value = restaurant.eta || '';

    // Show Google Places info if available
    if (restaurant.phone || restaurant.address || restaurant.website || restaurant.google_distance) {
        if (restaurant.phone) {
            phoneLink.href = `tel:${restaurant.phone}`;
            phoneLink.textContent = restaurant.phone;
        } else {
            phoneLink.textContent = 'N/A';
            phoneLink.removeAttribute('href');
        }

        document.getElementById('edit-address').textContent = restaurant.address || 'N/A';
        if (restaurant.website) {
            websiteLink.href = restaurant.website;
            websiteLink.textContent = restaurant.website;
        } else {
            websiteLink.textContent = 'N/A';
            websiteLink.removeAttribute('href');
        }

        const distanceText = restaurant.google_distance ? formatMetersToMiles(restaurant.google_distance) : 'N/A';
        const etaText = restaurant.eta ? formatETA(restaurant.eta) : '';
        document.getElementById('edit-google-distance').textContent = distanceText;
        document.getElementById('edit-eta').textContent = etaText;

        editPlaceInfo.classList.remove('hidden');
    } else {
        editPlaceInfo.classList.add('hidden');
    }

    elements.editModal.classList.remove('hidden');

    // Scroll modal to top
    const modalContent = elements.editModal.querySelector('.modal-content');
    if (modalContent) {
        modalContent.scrollTop = 0;
    }
}

// Close edit modal
function closeEditModal() {
    elements.editModal.classList.add('hidden');
    elements.editRestaurantForm.reset();
}

// Open stats modal
async function openStatsModal() {
    elements.statsModal.classList.remove('hidden');
    elements.statsContent.innerHTML = '<p class="loading-message">Loading stats...</p>';

    try {
        // Build query params based on current filters
        const params = new URLSearchParams();
        if (state.selectedCategory) {
            params.append('category', state.selectedCategory);
        }
        if (state.selectedDistance) {
            params.append('distance', state.selectedDistance);
        }

        const response = await fetch(`/api/randomize/stats?${params}`);
        const data = await response.json();

        if (data.success) {
            // Stats are merged directly into response, not nested under 'data'
            renderStats(data);
        } else {
            console.error('Stats API error:', data);
            elements.statsContent.innerHTML = '<p class="error-message">Failed to load stats</p>';
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
        elements.statsContent.innerHTML = '<p class="error-message">Failed to load stats</p>';
    }
}

// Close stats modal
function closeStatsModal() {
    elements.statsModal.classList.add('hidden');
}

// Render stats content
function renderStats(stats) {
    let html = '';

    // Show current filters
    if (stats.filters.category || stats.filters.distance) {
        html += '<div class="stats-info">';
        html += '<strong>Current Filters:</strong>';
        if (stats.filters.category) {
            html += `<p>Category: ${formatCategory(stats.filters.category)}</p>`;
        }
        if (stats.filters.distance) {
            html += `<p>Distance: ${stats.filters.distance.charAt(0).toUpperCase() + stats.filters.distance.slice(1).replace('-', ' ')}</p>`;
        }
        html += '</div>';
    }

    // Show excluded restaurant
    if (stats.excluded) {
        html += '<div class="stats-excluded">';
        html += `<strong>⏸️ Excluded:</strong> ${stats.excluded}<br>`;
        html += `<small>${stats.excluded_reason}</small>`;
        html += '</div>';
    }

    // Show closed restaurants
    if (stats.closed_today && stats.closed_today.length > 0) {
        html += '<div class="stats-closed">';
        html += `<strong>🚫 Closed Today:</strong> ${stats.closed_today.join(', ')}`;
        html += '</div>';
    }

    // Show pool info
    html += '<div class="stats-info">';
    html += `<strong>Total Pool Size:</strong> ${stats.total_pool_size} items`;
    html += '</div>';

    // Show items table
    html += '<table class="stats-table">';
    html += '<thead><tr><th>Restaurant</th><th>Count</th><th>Probability</th></tr></thead>';
    html += '<tbody>';

    stats.items.forEach(item => {
        const rowClass = item.excluded ? 'excluded-row' : '';
        html += `<tr class="${rowClass}">`;
        html += `<td>${item.name}`;
        if (item.excluded && item.excluded_reason) {
            html += `<br><small class="exclusion-reason">🚫 ${item.excluded_reason}</small>`;
        }
        html += `</td>`;
        html += `<td>${item.count}</td>`;
        html += `<td class="stats-percentage ${item.excluded ? 'excluded-percentage' : ''}">${item.percentage}%</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';

    elements.statsContent.innerHTML = html;
}

// Handle edit restaurant form submission
async function handleEditRestaurant(e) {
    e.preventDefault();

    const id = elements.editRestaurantId.value;
    const name = elements.editRestaurantName.value.trim();
    const distance = elements.editRestaurantDistance.value;

    // Get selected categories
    const categoryCheckboxes = elements.editCategoriesCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
    const categories = Array.from(categoryCheckboxes).map(cb => cb.value);

    // Get selected closed days
    const closedDaysCheckboxes = elements.editClosedDaysCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
    const closedDays = Array.from(closedDaysCheckboxes).map(cb => parseInt(cb.value));

    // Get Google Places data from hidden fields
    const placeId = elements.editPlaceIdInput.value || '';
    const phone = elements.editPhoneInput.value || '';
    const address = elements.editAddressInput.value || '';
    const website = elements.editWebsiteInput.value || '';
    const googleDistance = elements.editGoogleDistanceInput.value || '';
    const eta = elements.editEtaInput.value || '';

    if (!name) {
        showToast('Please enter a restaurant name', 'error');
        return;
    }

    if (categories.length === 0) {
        showToast('Please select at least one category', 'error');
        return;
    }

    try {
        const payload = {
            name,
            categories,
            distance,
            closed_days: closedDays,
            // Google Places data
            place_id: placeId,
            phone: phone,
            address: address,
            website: website,
            google_distance: googleDistance,
            eta: eta
        };

        console.log('Updating restaurant with payload:', payload);

        const response = await fetch(`/api/restaurants/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log('Update response:', data);

        if (data.success) {
            showToast(data.message || 'Restaurant updated!', 'success');
            closeEditModal();
            loadRestaurants();
        } else {
            showToast(data.error || 'Failed to update restaurant', 'error');
            console.error('Update failed:', data.error);
        }
    } catch (error) {
        console.error('Error updating restaurant:', error);
        showToast('Failed to update restaurant', 'error');
    }
}

// Handle delete from edit modal
async function handleDeleteFromEdit() {
    const id = elements.editRestaurantId.value;
    const name = elements.editRestaurantName.value;

    if (!confirm(`Remove "${name}" from the list?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/restaurants/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || 'Restaurant removed', 'success');
            closeEditModal();
            loadRestaurants();

            // Hide result if it was the deleted restaurant
            if (state.currentResult && state.currentResult.id === id) {
                elements.resultDisplay.classList.add('hidden');
            }
        } else {
            showToast(data.error || 'Failed to remove restaurant', 'error');
        }
    } catch (error) {
        console.error('Error deleting restaurant:', error);
        showToast('Failed to remove restaurant', 'error');
    }
}

// Handle add custom category
async function handleAddCategory() {
    const name = elements.newCategoryInput.value.trim().toLowerCase();

    if (!name) {
        showToast('Please enter a category name', 'error');
        return;
    }

    if (name.length < 2 || name.length > 30) {
        showToast('Category name must be between 2 and 30 characters', 'error');
        return;
    }

    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || 'Category added!', 'success');
            elements.newCategoryInput.value = '';
            await loadCategories(); // Reload categories to show new one
        } else {
            showToast(data.error || 'Failed to add category', 'error');
        }
    } catch (error) {
        console.error('Error adding category:', error);
        showToast('Failed to add category', 'error');
    }
}
