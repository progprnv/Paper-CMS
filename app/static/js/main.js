// Paper-CMS - Simple & Functional JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeFileUpload();
    initializeDataTables();
    initializeTooltips();
    initializeForms();
    initializeNotifications();
    
    console.log('Paper-CMS initialized successfully!');
});

// File Upload Enhancement
function initializeFileUpload() {
    const uploadZones = document.querySelectorAll('.file-upload, .file-upload-zone');
    
    uploadZones.forEach(zone => {
        const input = zone.querySelector('input[type="file"]');
        if (!input) return;
        
        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, () => zone.classList.add('drag-over'), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, () => zone.classList.remove('drag-over'), false);
        });
        
        zone.addEventListener('drop', handleDrop, false);
        zone.addEventListener('click', () => input.click());
        input.addEventListener('change', handleFileSelect);
        
        function handleDrop(e) {
            const files = e.dataTransfer.files;
            handleFiles(files);
        }
        
        function handleFileSelect(e) {
            const files = e.target.files;
            handleFiles(files);
        }
        
        function handleFiles(files) {
            Array.from(files).forEach(file => {
                if (validateFile(file)) {
                    displayFilePreview(file);
                }
            });
        }
        
        function validateFile(file) {
            const maxSize = 16 * 1024 * 1024; // 16MB
            const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            
            if (file.size > maxSize) {
                showNotification('File too large! Maximum size is 16MB.', 'warning');
                return false;
            }
            
            if (!allowedTypes.includes(file.type)) {
                showNotification('Invalid file type! Only PDF and Word documents are allowed.', 'warning');
                return false;
            }
            
            return true;
        }
        
        function displayFilePreview(file) {
            const preview = zone.querySelector('.file-preview') || createFilePreview();
            const fileSize = formatFileSize(file.size);
            
            preview.innerHTML = `
                <div class="d-flex align-items-center p-3 border rounded mb-2">
                    <i class="bi bi-file-earmark-text text-primary me-3" style="font-size: 1.5rem;"></i>
                    <div class="flex-grow-1">
                        <div class="fw-semibold">${file.name}</div>
                        <small class="text-muted">${fileSize}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="this.parentElement.parentElement.remove()">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
        }
        
        function createFilePreview() {
            const preview = document.createElement('div');
            preview.className = 'file-preview mt-3';
            zone.appendChild(preview);
            return preview;
        }
    });
}

// Data Tables Enhancement
function initializeDataTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        addTableSearch(table);
        addTableSorting(table);
        makeTableResponsive(table);
    });
}

function addTableSearch(table) {
    const wrapper = table.closest('.card-body') || table.parentElement;
    
    // Add search input
    const searchHTML = `
        <div class="mb-3">
            <div class="d-flex justify-content-between align-items-center">
                <div class="input-group" style="max-width: 300px;">
                    <span class="input-group-text"><i class="bi bi-search"></i></span>
                    <input type="text" class="form-control" placeholder="Search..." id="tableSearch">
                </div>
                <div class="btn-group" role="group">
                    <button class="btn btn-sm btn-outline-primary" onclick="exportTable('csv')">
                        <i class="bi bi-download me-1"></i>Export CSV
                    </button>
                </div>
            </div>
        </div>
    `;
    
    wrapper.insertAdjacentHTML('afterbegin', searchHTML);
    
    const searchInput = wrapper.querySelector('#tableSearch');
    searchInput.addEventListener('input', debounce(function(e) {
        filterTable(table, e.target.value);
    }, 300));
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

function addTableSorting(table) {
    const headers = table.querySelectorAll('th');
    
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.innerHTML += ' <i class="bi bi-arrow-down-up ms-1 opacity-50"></i>';
        
        header.addEventListener('click', () => {
            sortTable(table, index);
        });
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = table.dataset.sortOrder !== 'asc';
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        if (isAscending) {
            return aText.localeCompare(bText);
        } else {
            return bText.localeCompare(aText);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
}

function makeTableResponsive(table) {
    if (!table.closest('.table-responsive')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentElement.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }
}

// Form Enhancements
function initializeForms() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner me-2"></span>Processing...';
            }
        });
    });
    
    // Add real-time validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
        input.addEventListener('input', clearValidation);
    });
}

function validateInput(e) {
    const input = e.target;
    const value = input.value.trim();
    
    // Email validation
    if (input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showInputError(input, 'Please enter a valid email address');
            return;
        }
    }
    
    // Required field validation
    if (input.required && !value) {
        showInputError(input, 'This field is required');
        return;
    }
    
    clearInputError(input);
}

function clearValidation(e) {
    clearInputError(e.target);
}

function showInputError(input, message) {
    clearInputError(input);
    input.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    input.parentElement.appendChild(feedback);
}

function clearInputError(input) {
    input.classList.remove('is-invalid');
    const feedback = input.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

// Tooltip Initialization
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title') || this.getAttribute('data-bs-title');
            if (title) {
                showTooltip(this, title);
            }
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-custom';
    tooltip.textContent = text;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    tooltip.style.opacity = '1';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip-custom');
    if (tooltip) {
        tooltip.remove();
    }
}

// Notification System
function initializeNotifications() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-info-circle me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Add to page
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Utility Functions
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

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

function exportTable(format) {
    showNotification('Export functionality will be implemented soon!', 'info');
}

// Add custom CSS for notifications and tooltips
const style = document.createElement('style');
style.textContent = `
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
    }
    
    .notification-toast {
        margin-bottom: 10px;
        transition: opacity 0.3s ease;
    }
    
    .tooltip-custom {
        position: absolute;
        background: #333;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .tooltip-custom::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border: 5px solid transparent;
        border-top-color: #333;
    }
    
    .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid #f3f3f3;
        border-top: 2px solid var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

document.head.appendChild(style);