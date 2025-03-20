$(document).ready(function() {
    let searchTimeout;
    const searchDelay = 300; // Milliseconds to wait before searching

    // Function to sanitize user input
    function sanitizeInput(input) {
        return $('<div>').text(input).html();
    }

    // Function to perform search
    function performSearch(query) {
        if (!query || query.length > 100) return;
        
        const sanitizedQuery = sanitizeInput(query);
        
        $.get('/search', { q: sanitizedQuery }, function(results) {
            const $resultsList = $('#results-list');
            $resultsList.empty();
            
            if (results.length > 0) {
                results.forEach(function(article) {
                    const $item = $('<a>')
                        .addClass('list-group-item list-group-item-action')
                        .attr('href', '/article/' + article.id)
                        .html(`
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-1">${article.title}</h5>
                                <small class="text-muted">${new Date(article.updated_at).toLocaleDateString()}</small>
                            </div>
                        `);
                    $resultsList.append($item);
                });
                $('#search-results').removeClass('d-none');
            } else {
                $resultsList.html('<div class="list-group-item">No results found</div>');
                $('#search-results').removeClass('d-none');
            }
        });
    }

    // Handle main search form
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        const query = $('#search-input').val().trim();
        performSearch(query);
    });

    // Handle quick search input
    $('#quick-search').on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val().trim();
        
        searchTimeout = setTimeout(function() {
            performSearch(query);
        }, searchDelay);
    });

    // Handle quick search button click
    $('#quick-search-btn').on('click', function() {
        const query = $('#quick-search').val().trim();
        performSearch(query);
    });

    // Clear search results when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#search-results, #search-form, .quick-search').length) {
            $('#search-results').addClass('d-none');
        }
    });

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
});
