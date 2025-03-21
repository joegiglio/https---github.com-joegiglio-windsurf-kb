$(document).ready(function() {
    // Constants for validation
    const MAX_NAME_LENGTH = 100;
    const MAX_DESCRIPTION_LENGTH = 500;
    const NAME_PATTERN = /^[A-Za-z0-9\s\-_]+$/;

    // Function to sanitize user input
    function sanitizeInput(input) {
        if (!input) return '';
        return $('<div>').text(input).html()
            .replace(/[<>]/g, '') // Remove < and >
            .replace(/['"]/g, ''); // Remove quotes
    }

    // Function to validate input length
    function validateLength(input, maxLength) {
        return input.length > 0 && input.length <= maxLength;
    }

    // Function to show error message
    function showError(message) {
        const alert = $('<div>')
            .addClass('alert alert-danger alert-dismissible fade show')
            .html(`
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `);
        
        $('.container').prepend(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            alert.alert('close');
        }, 5000);
    }

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Initialize DataTables with responsive features
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries per page",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    }

    // Form validation for all admin forms
    $('form').on('submit', function(e) {
        const $form = $(this);
        let isValid = true;

        // Validate required fields
        $form.find('[required]').each(function() {
            const $field = $(this);
            const value = $field.val().trim();

            if (!value) {
                isValid = false;
                $field.addClass('is-invalid');
                showError(`${$field.prev('label').text()} is required.`);
            } else {
                $field.removeClass('is-invalid');
            }
        });

        // Validate field lengths
        $form.find('input[maxlength], textarea[maxlength]').each(function() {
            const $field = $(this);
            const value = $field.val().trim();
            const maxLength = parseInt($field.attr('maxlength'));

            if (value.length > maxLength) {
                isValid = false;
                $field.addClass('is-invalid');
                showError(`${$field.prev('label').text()} must not exceed ${maxLength} characters.`);
            }
        });

        // Validate patterns
        $form.find('input[pattern]').each(function() {
            const $field = $(this);
            const value = $field.val().trim();
            const pattern = new RegExp($field.attr('pattern'));

            if (value && !pattern.test(value)) {
                isValid = false;
                $field.addClass('is-invalid');
                showError(`${$field.prev('label').text()} contains invalid characters.`);
            }
        });

        if (!isValid) {
            e.preventDefault();
        }
    });

    // Real-time validation for inputs
    $('input, textarea').on('input', function() {
        const $field = $(this);
        const value = $field.val().trim();

        // Check required
        if ($field.prop('required') && !value) {
            $field.addClass('is-invalid');
            return;
        }

        // Check maxlength
        const maxLength = parseInt($field.attr('maxlength'));
        if (maxLength && value.length > maxLength) {
            $field.addClass('is-invalid');
            return;
        }

        // Check pattern
        const pattern = $field.attr('pattern');
        if (pattern && value && !new RegExp(pattern).test(value)) {
            $field.addClass('is-invalid');
            return;
        }

        $field.removeClass('is-invalid');
    });

    // Handle delete confirmations
    $('.delete-confirm').on('click', function(e) {
        e.preventDefault();
        const target = $(this).data('target');
        const message = $(this).data('message') || 'Are you sure you want to delete this item?';

        if (confirm(message)) {
            window.location.href = target;
        }
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);

    // Handle file uploads with preview
    $('.custom-file-input').on('change', function() {
        const fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').html(fileName);

        // Show image preview if it's an image
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            const preview = $(this).closest('form').find('.image-preview');

            reader.onload = function(e) {
                preview.attr('src', e.target.result);
            };

            reader.readAsDataURL(this.files[0]);
        }
    });

    // Handle dynamic form fields
    let fieldCounter = 0;
    $('.add-field').on('click', function() {
        fieldCounter++;
        const template = $(this).data('template');
        const container = $(this).data('container');
        const newField = template.replace(/\{index\}/g, fieldCounter);
        $(container).append(newField);
    });

    $(document).on('click', '.remove-field', function() {
        $(this).closest('.field-group').remove();
    });
});
