// Initialize Feather icons
feather.replace();

// Base API URL
const apiUrl = window.location.origin;

// Fetch data with error handling
async function fetchData(endpoint) {
    try {
        const response = await fetch(`${apiUrl}/api/${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// Show data details
async function showDetails(tableName, id) {
    const data = await fetchData(`table/${tableName}/${id}`);
    const chatWindow = document.querySelector('.chat-window');
    
    if (!data) {
        return;
    }

    const header = document.createElement('div');
    header.className = 'chat-header';
    header.innerHTML = `
        <button onclick="closeChatWindow()">
            <i data-feather="arrow-left"></i>
        </button>
        <h3>${tableName} Details</h3>
    `;

    const content = document.createElement('div');
    content.className = 'messages-container';
    
    Object.entries(data).forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = 'message-item';
        item.innerHTML = `
            <div class="message-content">
                <strong>${key}:</strong> 
                <span>${value}</span>
            </div>
        `;
        content.appendChild(item);
    });

    chatWindow.innerHTML = '';
    chatWindow.appendChild(header);
    chatWindow.appendChild(content);
    chatWindow.classList.remove('hidden');
    
    feather.replace();
}

// Close chat window
function closeChatWindow() {
    document.querySelector('.chat-window').classList.add('hidden');
}

// Show section
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
        section.classList.remove('active');
    });
    
    document.getElementById(sectionId).classList.remove('hidden');
    document.getElementById(sectionId).classList.add('active');
    
    closeChatWindow();

    // Load section specific data
    switch(sectionId) {
        case 'marketplace':
            loadTables();
            break;
        case 'requests':
            loadRelations();
            break;
        case 'archived':
            loadArchived();
            break;
        case 'chats':
            loadRecords();
            break;
    }
}

// Load tables
async function loadTables() {
    const tables = await fetchData('tables');
    const container = document.querySelector('.marketplace-list');
    container.innerHTML = '';
    
    if (tables && tables.length > 0) {
        tables.forEach(table => {
            const element = document.createElement('div');
            element.className = 'marketplace-item';
            element.innerHTML = `
                <i data-feather="table"></i>
                <div class="marketplace-details">
                    <span class="name">${table.name}</span>
                    <span class="preview">${table.count} records</span>
                </div>
            `;
            element.addEventListener('click', () => loadTableDetails(table.name));
            container.appendChild(element);
        });
        feather.replace();
    }
}

// Load relations
async function loadRelations() {
    const relations = await fetchData('relations');
    const container = document.querySelector('.request-list');
    container.innerHTML = '';
    
    if (relations) {
        Object.entries(relations).forEach(([table, keys]) => {
            const element = document.createElement('div');
            element.className = 'request-item';
            element.innerHTML = `
                <i data-feather="git-branch"></i>
                <div class="request-details">
                    <span class="name">${table}</span>
                    <span class="message">Primary Key: ${keys.primary_key}</span>
                    <span class="message">Foreign Keys: ${keys.foreign_keys.join(', ') || 'None'}</span>
                </div>
            `;
            container.appendChild(element);
        });
        feather.replace();
    }
}

// Load records
async function loadRecords() {
    const records = await fetchData('recent');
    const container = document.querySelector('.chat-list');
    container.innerHTML = '';
    
    if (records && records.length > 0) {
        records.forEach(record => {
            const element = document.createElement('div');
            element.className = 'chat-item';
            element.innerHTML = `
                <i data-feather="file-text"></i>
                <div class="chat-details">
                    <span class="name">${record.table}</span>
                    <span class="preview">ID: ${record.id}</span>
                </div>
                <span class="time">${record.timestamp}</span>
            `;
            element.addEventListener('click', () => showDetails(record.table, record.id));
            container.appendChild(element);
        });
        feather.replace();
    }
}

// Setup search
function setupSearch() {
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', debounce(async (e) => {
        const term = e.target.value.toLowerCase();
        if (term.length < 2) return;
        
        const results = await fetchData(`search?term=${encodeURIComponent(term)}`);
        const container = document.querySelector('.chat-list');
        container.innerHTML = '';
        
        if (results && results.length > 0) {
            results.forEach(result => {
                const element = document.createElement('div');
                element.className = 'chat-item';
                element.innerHTML = `
                    <i data-feather="search"></i>
                    <div class="chat-details">
                        <span class="name">${result.table}</span>
                        <span class="preview">${result.match}</span>
                    </div>
                `;
                element.addEventListener('click', () => showDetails(result.table, result.id));
                container.appendChild(element);
            });
            feather.replace();
        }
    }, 300));
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

    setupSearch();
    loadRecords(); // Load initial data
}

// Start the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);
