const API_BASE_URL = '/api';

// Update current time in header
function updateCurrentTime() {
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        const now = new Date();
        const timeString = now.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        timeElement.textContent = timeString;
    }
}

// Tab navigation functionality
function setupTabNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const activeContent = document.getElementById(tabName);
            if (activeContent) {
                activeContent.classList.add('active');
                
                // Load tab-specific data
                loadTabData(tabName);
            }
        });
    });
}

// Load data when tab is activated
function loadTabData(tabName) {
    switch(tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'documents':
            loadDocumentsList();
            break;
        case 'trading':
            refreshTradingData();
            break;
        case 'ledger':
            refreshLedgerData();
            break;
        case 'analytics':
            loadAnalyticsData();
            break;
    }
}

// Format currency
function formatCurrency(value) {
    if (!value) return '$0';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Format number
function formatNumber(value, decimals = 0) {
    if (!value) return '0';
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

// Format percentage
function formatPercentage(value, decimals = 1) {
    if (value === null || value === undefined) return '0%';
    return `${formatNumber(value, decimals)}%`;
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Modal functions
function showCreatePortfolioModal() {
    document.getElementById('createPortfolioModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('EcoLedger Pro initializing...');
    
    // Setup tab navigation
    setupTabNavigation();
    
    // Update time every second
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Load initial dashboard data
    loadDashboardData();
    
    // Setup form handlers
    setupFormHandlers();
    
    console.log('EcoLedger Pro initialized successfully');
});

// Setup all form handlers
function setupFormHandlers() {
    // Loan application form
    const loanForm = document.getElementById('loanApplicationForm');
    if (loanForm) {
        loanForm.addEventListener('submit', handleLoanApplicationSubmit);
    }
    
    // Document upload form
    const docForm = document.getElementById('documentUploadForm');
    if (docForm) {
        docForm.addEventListener('submit', handleDocumentUploadSubmit);
    }
    
    // Portfolio creation form
    const portfolioForm = document.getElementById('createPortfolioForm');
    if (portfolioForm) {
        portfolioForm.addEventListener('submit', handleCreatePortfolioSubmit);
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);