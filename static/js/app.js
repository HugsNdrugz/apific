// Initialize navigation and search functionality when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Initialize Feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        } else {
            console.warn('Feather Icons not loaded');
        }

        // Initialize navigation
        initializeNavigation();
        
        // Initialize search
        initializeSearch();
    } catch (error) {
        console.error('Error initializing app:', error);
    }
});

// Initialize navigation functionality
function initializeNavigation() {
    const navItems = document.querySelectorAll('.sidebar nav li');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update active state
            navItems.forEach(li => li.classList.remove('active'));
            item.classList.add('active');

            // Show corresponding section
            const sectionId = item.getAttribute('data-section');
            showSection(sectionId);
        });
    });
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchMessages, 300));
    }
}

// Show/hide sections
function showSection(sectionId) {
    if (!sectionId) {
        console.warn('No section ID provided');
        return;
    }

    // Hide all sections first
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
        section.classList.remove('active');
    });

    // Show the selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.classList.add('active');
    } else {
        console.warn(`Section with id "${sectionId}" not found`);
    }
}

// Search messages functionality
async function searchMessages() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchTerm = searchInput.value.trim();

    if (!searchTerm) {
        searchResults.innerHTML = '';
        return;
    }

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `search_term=${encodeURIComponent(searchTerm)}`
        });

        if (!response.ok) {
            throw new Error('Search request failed');
        }

        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching messages:', error);
        searchResults.innerHTML = '<p class="error">Error searching messages</p>';
    }
}

// Display search results
function displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');
    if (!results.length) {
        searchResults.innerHTML = '<p>No results found</p>';
        return;
    }

    const resultsList = results.map(result => `
        <li>
            <p>${result.text}</p>
            <small>${result.type} from ${result.name} at ${result.time}</small>
        </li>
    `).join('');

    searchResults.innerHTML = `<ul>${resultsList}</ul>`;
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Generic fetch helper with error handling
async function fetchContent(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.text();
    } catch (error) {
        console.error(`Error fetching ${url}:`, error);
        return `<p class="error-message">Error loading content. Please try again later.</p>`;
    }
}

// Helper function to safely replace Feather icons
function safeFeatherReplace() {
    try {
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    } catch (error) {
        console.warn('Error replacing Feather icons:', error);
    }
}

// Load calls
async function loadCalls() {
    const callsSection = document.getElementById('calls');
    if (callsSection) {
        const data = await fetchContent('/calls');
        callsSection.innerHTML = data;
        safeFeatherReplace();
    }
}

// Load keylogs
async function loadKeylogs() {
    const keylogsSection = document.getElementById('keylogs');
    if (keylogsSection) {
        const data = await fetchContent('/keylogs');
        keylogsSection.innerHTML = data;
        safeFeatherReplace();
    }
}

// Load contacts
async function loadContacts() {
    const contactsSection = document.getElementById('contacts');
    if (contactsSection) {
        const data = await fetchContent('/contacts');
        contactsSection.innerHTML = data;
        safeFeatherReplace();
    }
}

// Load chats
async function loadChats() {
    const chatsSection = document.getElementById('chats');
    if (chatsSection) {
        const data = await fetchContent('/');
        chatsSection.innerHTML = data;
        safeFeatherReplace();
    }
}