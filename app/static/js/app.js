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
    cooldownEndTime: null
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
    addCategoryBtn: null
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
}

// Check if user has a cookie
async function checkUser() {
    try {
        const response = await fetch('/api/user/check');
        const data = await response.json();

        if (data.exists && data.user) {
            state.user = data.user;
            elements.usernameDisplay.textContent = data.user;
            await loadCategories();
            loadRestaurants();
            loadHistory();
        } else {
            showWelcomeModal();
            await loadCategories(); // Load categories even for new users
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

    const name = document.createElement('h3');
    name.textContent = restaurant.name;

    const meta = document.createElement('div');
    meta.className = 'restaurant-meta';

    // Show all categories
    const categories = Array.isArray(restaurant.categories) ? restaurant.categories : [restaurant.category || 'quick'];
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

    const addedBy = document.createElement('span');
    addedBy.textContent = `Added by ${restaurant.added_by}`;
    meta.appendChild(addedBy);

    info.appendChild(name);
    info.appendChild(meta);

    card.appendChild(info);

    return card;
}

// Format category for display
function formatCategory(category) {
    // Handle null/undefined
    if (!category) return 'Unknown';

    if (category === 'sit-down') return 'Sit Down';
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
    elements.restaurantName.textContent = restaurant.name;

    // Show first category (or fallback)
    const categories = Array.isArray(restaurant.categories) ? restaurant.categories : [restaurant.category || 'quick'];
    const firstCategory = categories[0];
    elements.restaurantCategory.textContent = formatCategory(firstCategory);
    elements.restaurantCategory.className = `category-badge ${firstCategory}`;

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
    const distance = elements.restaurantDistanceInput.value;

    // Get selected categories from checkboxes
    const categoryCheckboxes = elements.addCategoriesCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
    const categories = Array.from(categoryCheckboxes).map(cb => cb.value);

    // Get selected closed days from checkboxes
    const closedDaysCheckboxes = elements.addClosedDaysCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
    const closedDays = Array.from(closedDaysCheckboxes).map(cb => parseInt(cb.value));

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
                closed_days: closedDays
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message || 'Restaurant added!', 'success');
            elements.addRestaurantForm.reset();
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
function showCooldownBanner(secondsRemaining) {
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
    elements.editRestaurantId.value = restaurant.id;
    elements.editRestaurantName.value = restaurant.name;
    elements.editRestaurantDistance.value = restaurant.distance || 'nearby';

    // Check the appropriate category checkboxes
    const categories = Array.isArray(restaurant.categories) ? restaurant.categories : [restaurant.category || 'quick'];
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

    elements.editModal.classList.remove('hidden');
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
            closed_days: closedDays
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
