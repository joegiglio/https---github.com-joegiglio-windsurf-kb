$(document).ready(function() {
    // Initialize TinyMCE
    function initTinyMCE(selector) {
        tinymce.init({
            selector: selector,
            height: 500,
            menubar: true,
            plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | blocks | ' +
                    'bold italic backcolor | alignleft aligncenter ' +
                    'alignright alignjustify | bullist numlist outdent indent | ' +
                    'image media | removeformat | help',
            content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
            branding: false,
            promotion: false,
            images_upload_url: '/admin/upload',
            images_upload_credentials: true,
            automatic_uploads: true,
            images_reuse_filename: true,
            image_advtab: true,
            image_dimensions: false,
            setup: function(editor) {
                editor.on('change', function() {
                    editor.save(); // Ensures form submission includes editor content
                });
            }
        });
    }

    // Initialize TinyMCE for both add and edit forms
    initTinyMCE('#articleContent');
    initTinyMCE('#editArticleContent');

    // Initialize DataTable
    const table = $('#articlesTable').DataTable({
        order: [[2, 'desc']],  // Sort by created date by default
        pageLength: 10,
        language: {
            search: "Filter articles:"
        }
    });

    // Add Article Form Submission
    $('#addArticleForm').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        formData.set('content', tinymce.get('articleContent').getContent());

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
            error: function(xhr) {
                alert('Failed to add article: ' + (xhr.responseJSON?.error || 'Unknown error'));
                console.error('Error adding article:', xhr.responseText);
            }
        });
    });

    // Edit Article Form Population
    $('.edit-article').on('click', function() {
        const btn = $(this);
        const id = btn.data('id');
        const title = btn.data('title');
        const content = btn.data('content');
        const categoryId = btn.data('category');
        
        $('#editArticleForm')
            .attr('action', `/admin/articles/${id}/edit`)
            .find('#editArticleTitle').val(title);
        $('#editArticleCategory').val(categoryId);
        tinymce.get('editArticleContent').setContent(content);
        $('#editArticleModal').modal('show');
    });

    // Edit Article Form Submission
    $('#editArticleForm').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        formData.set('content', tinymce.get('editArticleContent').getContent());

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
            error: function(xhr) {
                alert('Failed to update article: ' + (xhr.responseJSON?.error || 'Unknown error'));
                console.error('Error updating article:', xhr.responseText);
            }
        });
    });

    // Delete Article
    $('.delete-article').on('click', function() {
        const btn = $(this);
        if (confirm('Are you sure you want to delete this article? This action cannot be undone.')) {
            const id = btn.data('id');
            $.ajax({
                url: `/admin/articles/${id}/delete`,
                method: 'POST',
                success: function(response) {
                    location.reload();
                },
                error: function(xhr) {
                    alert('Failed to delete article: ' + (xhr.responseJSON?.error || 'Unknown error'));
                    console.error('Error deleting article:', xhr.responseText);
                }
            });
        }
    });
});
