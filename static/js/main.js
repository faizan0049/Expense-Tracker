/**
 * main.js
 * Main JavaScript file for the Personal Expense Tracker application
 * Contains utility functions and event handlers
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize date pickers with today's date if empty
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(function(picker) {
        if (!picker.value) {
            const today = new Date();
            const formattedDate = today.toISOString().substr(0, 10);
            picker.value = formattedDate;
        }
    });
    
    // Add event listener to category type select to filter categories
    const categoryTypeSelect = document.getElementById('type');
    if (categoryTypeSelect) {
        categoryTypeSelect.addEventListener('change', function() {
            // Change form styles based on category type
            const form = this.closest('form');
            const submitBtn = form.querySelector('button[type="submit"]');
            const headerEl = this.closest('.card').querySelector('.card-header');
            
            if (this.value === 'income') {
                headerEl.className = 'card-header bg-success text-white';
                submitBtn.className = 'btn btn-success';
            } else {
                headerEl.className = 'card-header bg-primary text-white';
                submitBtn.className = 'btn btn-primary';
            }
        });
    }
    
    // Handle modal confirmations
    const deleteConfirmBtns = document.querySelectorAll('.confirm-delete');
    deleteConfirmBtns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Number formatting for currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"].currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // Format currency displays
    const formatCurrency = function(value) {
        return 'Rs. ' + new Intl.NumberFormat('en-IN', {
            style: 'decimal',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    };
    
    // Update budget progress bars
    function updateBudgetProgressBars() {
        const progressBars = document.querySelectorAll('.budget-progress');
        progressBars.forEach(function(bar) {
            const spent = parseFloat(bar.getAttribute('data-spent'));
            const budget = parseFloat(bar.getAttribute('data-budget'));
            const percentage = Math.min(Math.round((spent / budget) * 100), 100);
            
            const progressBar = bar.querySelector('.progress-bar');
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            
            // Update color based on percentage
            if (percentage >= 100) {
                progressBar.className = 'progress-bar bg-danger';
            } else if (percentage >= 75) {
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-success';
            }
        });
    }
    
    // Call function if budget progress bars exist
    if (document.querySelector('.budget-progress')) {
        updateBudgetProgressBars();
    }
    
    // Set up mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== "#" && href.startsWith('#')) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add animation to cards on hover
    const animatedCards = document.querySelectorAll('.animated-card');
    animatedCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover');
        });
    });
    
    // Table row highlighting
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('table-active');
        });
        
        row.addEventListener('mouseleave', function() {
            this.classList.remove('table-active');
        });
    });
});
