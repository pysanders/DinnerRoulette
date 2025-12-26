// Global state
const state = {
    user: null,
    restaurants: [],
    selectedCategory: '',
    currentResult: null,
    currentEntryId: null,
    history: []
};

// DOM Elements
const elements = {
    welcomeModal: null,
    userRegistrationForm: null,
    firstNameInput: null,
    usernameDisplay: null,
    categoryButtons: null,
    spinButton: null,
    resultDisplay: null,
    restaurantName: null,
    restaurantCategory: null,
    restaurantAddedBy: null,
    addRestaurantForm: null,
    restaurantNameInput: null,
    restaurantCategoryInput: null,
    restaurantsList: null,
    restaurantCount: null,
    toast: null
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
    elements.categoryButtons = document.querySelectorAll('.category-btn');
    elements.spinButton = document.getElementById('spin-btn');
    elements.goingButton = document.getElementById('going-btn');
    elements.resultDisplay = document.getElementById('result-display');
    elements.restaurantName = document.getElementById('restaurant-name');
    elements.restaurantCategory = document.getElementById('restaurant-category');
    elements.restaurantAddedBy = document.getElementById('restaurant-added-by');
    elements.addRestaurantForm = document.getElementById('add-restaurant-form');
    elements.restaurantNameInput = document.getElementById('restaurant-name-input');
    elements.restaurantCategoryInput = document.getElementById('restaurant-category-input');
    elements.restaurantsList = document.getElementById('restaurants-list');
    elements.restaurantCount = document.getElementById('restaurant-count');
    elements.historyList = document.getElementById('history-list');
    elements.toast = document.getElementById('toast');
}

// Setup event listeners
function setupEventListeners() {
    // User registration
    elements.userRegistrationForm.addEventListener('submit', handleUserRegistration);

    // Category filter buttons
    elements.categoryButtons.forEach(btn => {
        btn.addEventListener('click', () => handleCategoryChange(btn.dataset.category));
    });

    // Spin button
    elements.spinButton.addEventListener('click', handleSpin);

    // Going button
    elements.goingButton.addEventListener('click', handleGoing);

    // Add restaurant form
    elements.addRestaurantForm.addEventListener('submit', handleAddRestaurant);
}

// Check if user has a cookie
async function checkUser() {
    try {
        const response = await fetch('/api/user/check');
        const data = await response.json();

        if (data.exists && data.user) {
            state.user = data.user;
            elements.usernameDisplay.textContent = data.user;
            loadRestaurants();
            loadHistory();
        } else {
            showWelcomeModal();
        }
    } catch (error) {
        console.error('Error checking user:', error);
        showWelcomeModal();
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

// Handle category change
function handleCategoryChange(category) {
    state.selectedCategory = category;

    // Update button states
    elements.categoryButtons.forEach(btn => {
        if (btn.dataset.category === category) {
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
        const url = state.selectedCategory
            ? `/api/restaurants?category=${state.selectedCategory}`
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

    const info = document.createElement('div');
    info.className = 'restaurant-info';

    const name = document.createElement('h3');
    name.textContent = restaurant.name;

    const meta = document.createElement('div');
    meta.className = 'restaurant-meta';

    const badge = document.createElement('span');
    badge.className = `category-badge ${restaurant.category}`;
    badge.textContent = formatCategory(restaurant.category);

    const addedBy = document.createElement('span');
    addedBy.textContent = `Added by ${restaurant.added_by}`;

    meta.appendChild(badge);
    meta.appendChild(addedBy);

    info.appendChild(name);
    info.appendChild(meta);

    // Delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn btn-danger';
    deleteBtn.textContent = 'Remove';
    deleteBtn.onclick = () => handleDeleteRestaurant(restaurant.id, restaurant.name);

    card.appendChild(info);
    card.appendChild(deleteBtn);

    return card;
}

// Format category for display
function formatCategory(category) {
    if (category === 'sit-down') return 'Sit Down';
    return category.charAt(0).toUpperCase() + category.slice(1);
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
        const url = state.selectedCategory
            ? `/api/randomize?category=${state.selectedCategory}`
            : '/api/randomize';

        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.restaurant) {
            state.currentResult = data.restaurant;
            state.currentEntryId = data.entry_id;
            showResult(data.restaurant);
            loadHistory(); // Reload history to show the new spin
        } else {
            showToast(data.error || 'No restaurants available', 'error');
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
    elements.restaurantName.textContent = restaurant.name;
    elements.restaurantCategory.textContent = formatCategory(restaurant.category);
    elements.restaurantCategory.className = `category-badge ${restaurant.category}`;
    elements.restaurantAddedBy.textContent = restaurant.added_by;
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
    const category = elements.restaurantCategoryInput.value;

    if (!name || !category) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    try {
        const response = await fetch('/api/restaurants', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, category })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || 'Restaurant added!', 'success');
            elements.addRestaurantForm.reset();
            loadRestaurants();
        } else {
            showToast(data.error || 'Failed to add restaurant', 'error');
        }
    } catch (error) {
        console.error('Error adding restaurant:', error);
        showToast('Failed to add restaurant', 'error');
    }
}

// Handle delete restaurant
async function handleDeleteRestaurant(id, name) {
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

// Format timestamp to relative time
function formatTimeAgo(timestamp) {
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now - then) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

    return then.toLocaleDateString();
}
