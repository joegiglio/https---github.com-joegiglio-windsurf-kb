$(document).ready(function() {
    // Constants
    const SEARCH_DELAY = 300;
    const MAX_QUERY_LENGTH = 100;
    const MIN_QUERY_LENGTH = 2;
    
    // Cache DOM elements
    const $searchForm = $('#search-form');
    const $searchInput = $('#search-input');
    const $searchResults = $('#search-results');
    const $resultsList = $('#results-list');
    
    let searchTimeout;
    let lastLoggedSearch = '';

    // Function to sanitize user input
    function sanitizeInput(input) {
        return $('<div>').text(input).html()
            .replace(/[<>]/g, '') // Remove < and >
            .replace(/['"]/g, ''); // Remove quotes
    }

    // Function to validate search input
    function validateSearchInput(query) {
        if (!query || typeof query !== 'string') {
            return false;
        }
        
        query = query.trim();
        return query.length >= MIN_QUERY_LENGTH && query.length <= MAX_QUERY_LENGTH;
    }

    // Function to format date
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Function to create search result item
    function createSearchResultItem(article) {
        return $('<a>')
            .addClass('list-group-item list-group-item-action')
            .attr('href', `/article/${article.id}`)
            .html(`
                <div class="d-flex w-100 justify-content-between">
                    <div class="search-result-content">
                        <h5 class="mb-1">${sanitizeInput(article.title)}</h5>
                        <p class="mb-1 text-muted">${sanitizeInput(article.preview)}</p>
                        <small class="category-tag">${sanitizeInput(article.category_name)}</small>
                    </div>
                    <small class="text-muted text-end">
                        ${formatDate(article.updated_at)}
                    </small>
                </div>
            `);
    }

    // Function to perform search
    function performSearch(query, shouldLog = false) {
        if (!validateSearchInput(query)) {
            return;
        }

        const sanitizedQuery = sanitizeInput(query);
        
        $.ajax({
            url: '/search',
            method: 'GET',
            data: { 
                q: sanitizedQuery,
                log: shouldLog  // Only log when explicitly requested
            },
            beforeSend: function() {
                $resultsList.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
                $searchResults.removeClass('d-none');
            },
            success: function(results) {
                $resultsList.empty();
                
                if (results.length > 0) {
                    results.forEach(function(article) {
                        $resultsList.append(createSearchResultItem(article));
                    });
                } else {
                    $resultsList.html(`
                        <div class="text-center p-4">
                            <i class="bi bi-search fs-2 text-muted"></i>
                            <p class="mt-3">No results found for "${sanitizeInput(query)}"</p>
                            <p class="text-muted">Try adjusting your search terms or browse our categories below</p>
                        </div>
                    `);
                }
            },
            error: function() {
                $resultsList.html(`
                    <div class="alert alert-danger" role="alert">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        An error occurred while searching. Please try again later.
                    </div>
                `);
            }
        });
    }

    // Handle search form submission
    $searchForm.on('submit', function(e) {
        e.preventDefault();
        const query = $searchInput.val().trim();
        performSearch(query, true);  // Always log on form submission
        lastLoggedSearch = query;
    });

    // Handle search input with debouncing
    $searchInput.on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val().trim();
        
        if (query.length >= MIN_QUERY_LENGTH) {
            searchTimeout = setTimeout(function() {
                performSearch(query, false);  // Don't log during typing
            }, SEARCH_DELAY);
        } else {
            $searchResults.addClass('d-none');
        }
    });

    // Close search results when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#search-results, #search-form').length) {
            $searchResults.addClass('d-none');
        }
    });

    // Initialize Bootstrap tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Add responsive behavior for mobile devices
    if ($(window).width() < 768) {
        $('.category-card').addClass('mb-3');
    }

    // Handle window resize events
    $(window).on('resize', function() {
        if ($(window).width() < 768) {
            $('.category-card').addClass('mb-3');
        } else {
            $('.category-card').removeClass('mb-3');
        }
    });
});
