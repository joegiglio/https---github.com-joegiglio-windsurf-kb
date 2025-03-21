/**
 * Utility functions for admin interface
 */

// Input validation functions
function validateLength(value, maxLength) {
    return value && value.length > 0 && value.length <= maxLength;
}

function sanitizeInput(text) {
    if (!text) return '';
    
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show">
            ${sanitizeInput(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert alert at the top of the content area
    const contentArea = document.querySelector('.content-area') || document.body;
    contentArea.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}
