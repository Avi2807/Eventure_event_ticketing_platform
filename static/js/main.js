// Main JavaScript file

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Set current user for templates
    if (token && user) {
        window.current_user = user;
    }
});

// API helper function
async function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }
    
    const options = {
        method: method,
        headers: headers
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="spinner"></div>';
}

// Show error message
function showError(element, message) {
    element.innerHTML = `<div class="alert alert-error">${message}</div>`;
}

// Logout function
function logout() {
    // Confirm logout
    if (confirm('Are you sure you want to logout?')) {
        // Clear localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        
        // Clear any session data
        sessionStorage.clear();
        
        // Optionally call server-side logout endpoint
        fetch('/logout', {
            method: 'GET',
            credentials: 'same-origin'
        }).catch(err => {
            console.log('Logout endpoint call failed (non-critical):', err);
        });
        
        // Redirect to home page
        window.location.href = '/';
    }
}


