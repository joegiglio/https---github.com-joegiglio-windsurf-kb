$(document).ready(function() {
    // Initialize TinyMCE for all rich editors
    tinymce.init({
        selector: '.rich-editor',
        height: 400,
        plugins: [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
            'insertdatetime', 'media', 'table', 'help', 'wordcount'
        ],
        toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link image | code',
        menubar: false,
        branding: false,
        setup: function(editor) {
            editor.on('change', function() {
                editor.save();
            });
        }
    });

    // Edit article
    $('.edit-article').click(function() {
        const id = $(this).data('id');
        const title = $(this).data('title');
        const content = $(this).data('content'); // Don't decode HTML - TinyMCE expects raw HTML
        const keywords = $(this).data('keywords');
        const categoryId = $(this).data('category');

        $('#editArticleForm').attr('action', `/admin/articles/${id}/edit`);
        $('#editTitle').val(title);
        $('#editCategory').val(categoryId);
        $('#editKeywords').val(keywords);
        
        // Need to wait for TinyMCE to be ready
        setTimeout(function() {
            const editor = tinymce.get('editContent');
            if (editor) {
                editor.setContent(content);
            }
        }, 100);
    });

    // Delete article
    $('.delete-article').click(function() {
        const id = $(this).data('id');
        const title = $(this).data('title');
        
        $('#deleteArticleTitle').text(title);
        $('#deleteArticleForm').attr('action', `/admin/articles/${id}/delete`);
    });

    // Form submission
    $('#editArticleForm').submit(function(e) {
        e.preventDefault();
        
        // Get content from TinyMCE before form submission
        const editor = tinymce.get('editContent');
        if (editor) {
            $('#editContent').val(editor.getContent());
        }
        
        const form = $(this);
        const formData = new FormData(form[0]);

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#editArticleModal').modal('hide');
                location.reload();
            },
            error: function(xhr, status, error) {
                alert('An error occurred while saving the article');
                console.error('Error:', error);
            }
        });
    });

    // Add article form submission
    $('#addArticleModal form').submit(function(e) {
        e.preventDefault();
        
        // Get content from TinyMCE before form submission
        const editor = tinymce.get('content');
        if (editor) {
            $('#content').val(editor.getContent());
        }
        
        const form = $(this);
        const formData = new FormData(form[0]);

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#addArticleModal').modal('hide');
                location.reload();
            },
            error: function(xhr, status, error) {
                alert('An error occurred while adding the article');
                console.error('Error:', error);
            }
        });
    });

    // Delete form submission
    $('#deleteArticleForm').submit(function(e) {
        e.preventDefault();
        const form = $(this);

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            success: function(response) {
                $('#deleteArticleModal').modal('hide');
                location.reload();
            },
            error: function(xhr, status, error) {
                alert('An error occurred while deleting the article');
                console.error('Error:', error);
            }
        });
    });
});
