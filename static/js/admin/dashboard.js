$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Auto-refresh dashboard data every 5 minutes
    function refreshDashboard() {
        $.get('/admin/dashboard-data', function(data) {
            // Update statistics
            $('.stats-categories').text(data.categories_count);
            $('.stats-articles').text(data.articles_count);
            $('.stats-views').text(data.total_views);
            $('.stats-searches').text(data.total_searches);

            // Update recent articles
            const articlesTable = $('#recentArticles tbody');
            articlesTable.empty();
            data.recent_articles.forEach(function(article) {
                articlesTable.append(`
                    <tr>
                        <td>
                            <a href="/article/${article.id}" target="_blank">
                                ${sanitizeInput(article.title)}
                            </a>
                        </td>
                        <td>${sanitizeInput(article.category_name)}</td>
                        <td>${article.created_at}</td>
                    </tr>
                `);
            });

            // Update popular searches
            const searchesTable = $('#popularSearches tbody');
            searchesTable.empty();
            data.popular_searches.forEach(function(search) {
                searchesTable.append(`
                    <tr>
                        <td>${sanitizeInput(search.term)}</td>
                        <td>${search.count}</td>
                        <td>${search.last_searched}</td>
                    </tr>
                `);
            });
        });
    }

    // Refresh every 5 minutes
    setInterval(refreshDashboard, 300000);
});
