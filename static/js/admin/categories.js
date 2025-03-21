$(document).ready(function() {
    // Initialize Sortable for category reordering
    const categoryList = document.getElementById('categoryList');
    if (categoryList) {
        new Sortable(categoryList, {
            handle: '.handle',
            animation: 150,
            onEnd: function() {
                // Get the new order of categories
                const categoryOrder = [];
                $('#categoryList tr').each(function() {
                    categoryOrder.push(parseInt($(this).data('id')));
                });

                // Send the new order to the server
                $.ajax({
                    url: '/admin/categories/reorder',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ categories: categoryOrder }),
                    success: function(response) {
                        showToast('success', 'Categories reordered successfully');
                    },
                    error: function(xhr) {
                        showToast('error', 'Failed to reorder categories');
                        console.error('Error reordering categories:', xhr.responseText);
                    }
                });
            }
        });
    }

    // Initialize DataTable with ordering disabled (we're using drag-and-drop instead)
    const table = $('#categoriesTable').DataTable({
        ordering: false,
        pageLength: 10,
        language: {
            search: "Filter categories:"
        }
    });

    // Form validation function
    function validateCategoryForm(form) {
        const nameInput = form.find('input[name="name"]');
        const name = nameInput.val().trim();
        
        if (name.length === 0 || name.length > 100) {
            showToast('error', 'Category name must be between 1 and 100 characters');
            return false;
        }
        
        if (!/^[A-Za-z0-9\s\-_]+$/.test(name)) {
            showToast('error', 'Category name can only contain letters, numbers, spaces, hyphens, and underscores');
            return false;
        }
        
        const description = form.find('textarea[name="description"]').val().trim();
        if (description.length > 500) {
            showToast('error', 'Description must not exceed 500 characters');
            return false;
        }
        
        return true;
    }

    // Add Category Form Submission
    $('#addCategoryForm').on('submit', function(e) {
        e.preventDefault();
        
        if (!validateCategoryForm($(this))) {
            return;
        }

        const form = $(this);
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                location.reload();
            },
            error: function(xhr) {
                showToast('error', 'Failed to add category');
                console.error('Error adding category:', xhr.responseText);
            }
        });
    });

    // Edit Category
    $('.edit-category').on('click', function() {
        const btn = $(this);
        const id = btn.data('id');
        const name = btn.data('name');
        const description = btn.data('description');
        
        $('#editCategoryForm')
            .attr('action', `/admin/categories/${id}/edit`)
            .find('#editCategoryName').val(name);
        $('#editCategoryDescription').val(description);
        $('#editCategoryModal').modal('show');
    });

    // Edit Category Form Submission
    $('#editCategoryForm').on('submit', function(e) {
        e.preventDefault();
        
        if (!validateCategoryForm($(this))) {
            return;
        }

        const form = $(this);
        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            success: function(response) {
                location.reload();
            },
            error: function(xhr) {
                showToast('error', 'Failed to update category');
                console.error('Error updating category:', xhr.responseText);
            }
        });
    });

    // Delete Category
    $('.delete-category').on('click', function() {
        const btn = $(this);
        if (btn.prop('disabled')) {
            showToast('error', 'Cannot delete category with existing articles');
            return;
        }

        if (confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
            const id = btn.data('id');
            $.ajax({
                url: `/admin/categories/${id}/delete`,
                method: 'POST',
                success: function(response) {
                    location.reload();
                },
                error: function(xhr) {
                    showToast('error', 'Failed to delete category');
                    console.error('Error deleting category:', xhr.responseText);
                }
            });
        }
    });

    // Helper function to show toast messages
    function showToast(type, message) {
        const toast = $('<div>')
            .addClass('toast position-fixed bottom-0 end-0 m-3')
            .attr('role', 'alert')
            .attr('aria-live', 'assertive')
            .attr('aria-atomic', 'true');

        const toastHeader = $('<div>')
            .addClass('toast-header bg-' + (type === 'error' ? 'danger' : 'success') + ' text-white');

        const toastTitle = $('<strong>')
            .addClass('me-auto')
            .text(type === 'error' ? 'Error' : 'Success');

        const closeButton = $('<button>')
            .addClass('btn-close')
            .attr('type', 'button')
            .attr('data-bs-dismiss', 'toast');

        const toastBody = $('<div>')
            .addClass('toast-body')
            .text(message);

        toastHeader.append(toastTitle, closeButton);
        toast.append(toastHeader, toastBody);
        $('body').append(toast);

        const bsToast = new bootstrap.Toast(toast[0], {
            autohide: true,
            delay: 3000
        });
        bsToast.show();

        toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }
});
