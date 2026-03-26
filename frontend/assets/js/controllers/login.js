/**
 * @author Eidan Khan
 */
$(document).ready(function () {
    $('#login-form').on('submit', async function (e) {
        e.preventDefault();

        const btn = $('#login-btn');
        const alertBox = $('#login-alert');

        btn.prop('disabled', true).text('Signing in...');
        alertBox.addClass('d-none');

        const email = $('#email').val();
        const password = $('#password').val();

        try {
            const data = await AuthService.login(email, password);

            if (data && data.access_token) {
                // CHANGED: Use sessionStorage to match your adminService.js
                sessionStorage.setItem('access_token', data.access_token);
                sessionStorage.setItem('user_role', data.role);
                sessionStorage.setItem('name', data.name);


                // Redirect logic
                if (data.role === 'ADMIN') {
                    // Optional but good for consistency
                    sessionStorage.setItem('admin_session', 'active');
                    window.location.href = 'admin.html'; // Removed leading slash for consistency
                } else {
                    window.location.href = 'dashboard.html';
                }
            }

        } catch (error) {
            alertBox.text(error).removeClass('d-none');
            btn.prop('disabled', false).text('Sign In');
        }
    });
});