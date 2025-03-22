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
                'insertdatetime', 'media', 'table', 'help', 'wordcount', 'paste'
            ],
            toolbar: 'undo redo | formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | removeformat | help',
            content_style: '@import url("/static/css/article.css");',
            branding: false,
            promotion: false,
            images_upload_url: '/admin/upload',
            images_upload_credentials: true,
            automatic_uploads: true,
            convert_urls: false,
            relative_urls: false,
            remove_script_host: false,
            style_formats: [
                { title: 'Text align', items: [
                    { title: 'Left', format: 'alignleft', classes: 'text-left' },
                    { title: 'Center', format: 'aligncenter', classes: 'text-center' },
                    { title: 'Right', format: 'alignright', classes: 'text-right' },
                    { title: 'Justify', format: 'alignjustify', classes: 'text-justify' }
                ]},
                { title: 'Image', items: [
                    { title: 'Responsive', selector: 'img', classes: 'img-fluid' }
                ]}
            ],
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
