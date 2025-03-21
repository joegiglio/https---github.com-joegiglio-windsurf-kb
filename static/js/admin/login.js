$(document).ready(function() {
    const USERNAME_MAX_LENGTH = 50;
    const USERNAME_PATTERN = /^[A-Za-z0-9\-_]+$/;

    // Toggle password visibility
    $('#togglePassword').on('click', function() {
        const $password = $('#password');
        const $icon = $(this).find('i');
        
        if ($password.attr('type') === 'password') {
            $password.attr('type', 'text');
            $icon.removeClass('bi-eye').addClass('bi-eye-slash');
        } else {
            $password.attr('type', 'password');
            $icon.removeClass('bi-eye-slash').addClass('bi-eye');
        }
    });

    // Form validation
    $('#loginForm').on('submit', function(e) {
        const username = $('#username').val().trim();
        const password = $('#password').val();
        let isValid = true;

        // Validate username
        if (!username || !USERNAME_PATTERN.test(username) || username.length > USERNAME_MAX_LENGTH) {
            $('#username').addClass('is-invalid');
            isValid = false;
        } else {
            $('#username').removeClass('is-invalid');
        }

        // Validate password
        if (!password) {
            $('#password').addClass('is-invalid');
            isValid = false;
        } else {
            $('#password').removeClass('is-invalid');
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    // Real-time username validation
    $('#username').on('input', function() {
        const value = $(this).val().trim();
        if (!value || !USERNAME_PATTERN.test(value) || value.length > USERNAME_MAX_LENGTH) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
});
