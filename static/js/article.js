$(document).ready(function() {
    function updateRatingUI(data) {
        console.log('Updating UI with data:', data);
        $('.upvote-count').text(data.upvotes);
        $('.downvote-count').text(data.downvotes);
        $('.percentage-value').text(data.rating_percentage);
    }

    function rateArticle(articleId, voteType) {
        console.log('Sending vote:', { articleId, voteType });
        $.ajax({
            url: `/article/${articleId}/rate`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ vote: voteType }),
            success: function(response) {
                console.log('Vote successful:', response);
                updateRatingUI(response);
                
                // Disable both buttons after voting
                $('#upvote-btn, #downvote-btn').prop('disabled', true);
                
                // Show thank you message
                const message = $('<div>')
                    .addClass('alert alert-success mt-3')
                    .text('Thank you for your feedback!');
                $('#rating-section').append(message);
                
                // Store vote in localStorage
                localStorage.setItem(`article-${articleId}-voted`, 'true');
            },
            error: function(xhr, status, error) {
                console.error('Vote failed:', { status, error, response: xhr.responseText });
                const errorMsg = $('<div>')
                    .addClass('alert alert-danger mt-3')
                    .text('An error occurred. Please try again later.');
                $('#rating-section').append(errorMsg);
            }
        });
    }

    // Check if user has already voted
    const articleId = $('#upvote-btn').data('article-id');
    if (localStorage.getItem(`article-${articleId}-voted`)) {
        $('#upvote-btn, #downvote-btn').prop('disabled', true);
    }

    $('#upvote-btn').click(function() {
        const articleId = $(this).data('article-id');
        console.log('Upvote clicked for article:', articleId);
        rateArticle(articleId, 'up');
    });

    $('#downvote-btn').click(function() {
        const articleId = $(this).data('article-id');
        console.log('Downvote clicked for article:', articleId);
        rateArticle(articleId, 'down');
    });
});
