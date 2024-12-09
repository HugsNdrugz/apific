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
    }

    // Load section specific data
    loadSectionData(sectionId);
}

// Load section data
async function loadSectionData(sectionId) {
    switch(sectionId) {
        case 'calls':
            await loadCalls();
            break;
        case 'archived':
            await loadArchived();
            break;
        case 'keylogs':
            await loadKeylogs();
            break;
        case 'contacts':
            await loadContacts();
            break;
        case 'chats':
            await loadChats();
            break;
    }
}

// Load calls
async function loadCalls() {
    const response = await fetch('/calls');
    const data = await response.text();
    document.getElementById('calls').innerHTML = data;
    feather.replace();
}

// Load archived
async function loadArchived() {
    const response = await fetch('/archived');
    const data = await response.text();
    document.getElementById('archived').innerHTML = data;
    feather.replace();
}

// Load keylogs
async function loadKeylogs() {
    const response = await fetch('/keylogs');
    const data = await response.text();
    document.getElementById('keylogs').innerHTML = data;
    feather.replace();
}

// Load contacts
async function loadContacts() {
    const response = await fetch('/contacts');
    const data = await response.text();
    document.getElementById('contacts').innerHTML = data;
    feather.replace();
}

// Load chats
async function loadChats() {
    const response = await fetch('/');
    const data = await response.text();
    document.getElementById('chats').innerHTML = data;
    feather.replace();
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