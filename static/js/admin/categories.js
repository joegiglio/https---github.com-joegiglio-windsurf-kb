$(document).ready(function() {
    // Constants for validation
    const MAX_NAME_LENGTH = 100;
    const MAX_DESCRIPTION_LENGTH = 500;
    const NAME_PATTERN = /^[A-Za-z0-9\s\-_]+$/;

    // Initialize DataTable
    $('#categoriesTable').DataTable({
        order: [[0, 'asc']],
        pageLength: 10,
        language: {
            search: "Filter categories:"
        },
        responsive: true
    });

    // Handle edit category button
    $('.edit-category').on('click', function() {
        const categoryId = $(this).data('category-id');
        const categoryName = $(this).data('category-name');
        const categoryDescription = $(this).data('category-description');
        
        $('#editCategoryId').val(categoryId);
        $('#editCategoryName').val(categoryName);
        $('#editCategoryDescription').val(categoryDescription);
        $('#editCategoryForm').attr('action', `/admin/categories/${categoryId}/edit`);
        $('#editCategoryModal').modal('show');
    });

    // Handle delete category button
    $('.delete-category').on('click', function() {
        const categoryId = $(this).data('category-id');
        const categoryName = $(this).data('category-name');
        
        $('#deleteCategoryName').text(categoryName);
        $('#deleteCategoryForm').attr('action', `/admin/categories/${categoryId}/delete`);
        $('#deleteCategoryModal').modal('show');
    });

    // Form validation
    function validateCategoryForm(form) {
        const nameInput = form.find('input[name="name"]');
        const name = nameInput.val().trim();
        
        if (!validateLength(name, MAX_NAME_LENGTH)) {
            showError('Category name must be between 1 and 100 characters.');
            return false;
        }
        
        if (!NAME_PATTERN.test(name)) {
            showError('Category name can only contain letters, numbers, spaces, hyphens, and underscores.');
            return false;
        }
        
        const description = form.find('textarea[name="description"]').val().trim();
        if (!validateLength(description, MAX_DESCRIPTION_LENGTH)) {
            showError('Description must not exceed 500 characters.');
            return false;
        }
        
        return true;
    }

    // Add form validation
    $('#addCategoryForm').on('submit', function(e) {
        if (!validateCategoryForm($(this))) {
            e.preventDefault();
        }
    });

    // Edit form validation
    $('#editCategoryForm').on('submit', function(e) {
        if (!validateCategoryForm($(this))) {
            e.preventDefault();
        }
    });

    // Real-time validation for category name
    $('input[name="name"]').on('input', function() {
        const $input = $(this);
        const value = $input.val().trim();
        
        if (!validateLength(value, MAX_NAME_LENGTH) || !NAME_PATTERN.test(value)) {
            $input.addClass('is-invalid');
        } else {
            $input.removeClass('is-invalid');
        }
    });

    // Real-time validation for description
    $('textarea[name="description"]').on('input', function() {
        const $input = $(this);
        const value = $input.val().trim();
        
        if (!validateLength(value, MAX_DESCRIPTION_LENGTH)) {
            $input.addClass('is-invalid');
        } else {
            $input.removeClass('is-invalid');
        }
    });
});
