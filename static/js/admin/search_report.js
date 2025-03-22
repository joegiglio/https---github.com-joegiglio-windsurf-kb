$(document).ready(function() {
    // Initialize variables
    let currentData = [];
    
    // Function to format date
    function formatDate(date) {
        return new Date(date).toLocaleString();
    }
    
    // Function to update table with filtered data
    function updateTable(data) {
        const $tbody = $('#searchTable tbody');
        $tbody.empty();
        
        data.forEach(function(search) {
            $tbody.append(`
                <tr>
                    <td>${$('<div>').text(search.term).html()}</td>
                    <td>${search.results_count}</td>
                    <td>${formatDate(search.created_at)}</td>
                    <td>${$('<div>').text(search.ip_address).html()}</td>
                </tr>
            `);
        });
        
        // Update statistics
        const totalSearches = data.length;
        const totalResults = data.reduce((sum, search) => sum + search.results_count, 0);
        const avgResults = totalSearches > 0 ? (totalResults / totalSearches).toFixed(1) : '0.0';
        const noResults = data.filter(search => search.results_count === 0).length;
        const noResultsRate = totalSearches > 0 ? ((noResults / totalSearches) * 100).toFixed(1) : '0.0';
        
        $('#totalSearches').text(totalSearches);
        $('#avgResults').text(avgResults);
        $('#noResultsRate').text(noResultsRate + '%');
    }
    
    // Filter searches based on search term
    $('#searchFilter').on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        const filteredData = currentData.filter(search => 
            search.term.toLowerCase().includes(searchTerm)
        );
        updateTable(filteredData);
    });
    
    // Time period filters
    function filterByDays(days) {
        const now = new Date();
        const cutoff = new Date(now - (days * 24 * 60 * 60 * 1000));
        
        return currentData.filter(search => 
            new Date(search.created_at) > cutoff
        );
    }
    
    $('#last7Days').click(function() {
        $(this).addClass('active').siblings().removeClass('active');
        updateTable(filterByDays(7));
    });
    
    $('#last30Days').click(function() {
        $(this).addClass('active').siblings().removeClass('active');
        updateTable(filterByDays(30));
    });
    
    $('#allTime').click(function() {
        $(this).addClass('active').siblings().removeClass('active');
        updateTable(currentData);
    });
    
    // Export to CSV
    $('#exportCsv').click(function() {
        const rows = [
            ['Search Term', 'Results', 'Date', 'IP Address']
        ];
        
        currentData.forEach(function(search) {
            rows.push([
                search.term,
                search.results_count,
                formatDate(search.created_at),
                search.ip_address
            ]);
        });
        
        let csvContent = "data:text/csv;charset=utf-8," + 
            rows.map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
            
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "search_report.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
    
    // Load initial data
    $.get('/admin/api/search-logs', function(data) {
        currentData = data;
        updateTable(currentData);
        $('#allTime').addClass('active');
    });
});
