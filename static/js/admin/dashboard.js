$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Initialize search metrics chart
    let searchMetricsChart = null;

    function initializeSearchMetricsChart(data) {
        const ctx = document.getElementById('searchMetricsChart').getContext('2d');
        if (searchMetricsChart) {
            searchMetricsChart.destroy();
        }
        
        searchMetricsChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Searches with Results', 'Searches without Results'],
                datasets: [{
                    data: [data.with_results, data.no_results],
                    backgroundColor: ['#4e73df', '#e74a3b'],
                    hoverBackgroundColor: ['#2e59d9', '#be2617'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)",
                }]
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                cutout: '0%'
            }
        });
    }

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

            // Update search metrics chart
            if (data.search_metrics) {
                initializeSearchMetricsChart(data.search_metrics);
            }
        });
    }

    // Initial load
    refreshDashboard();

    // Refresh every 5 minutes
    setInterval(refreshDashboard, 300000);

    // Helper function to sanitize input
    function sanitizeInput(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
});
