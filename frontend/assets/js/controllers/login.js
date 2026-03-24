/**
 * @author Eidan Khan
 */
$(document).ready(function() {
    
    $('#login-form').on('submit', async function(e) {
        e.preventDefault();
        
        const btn = $('#login-btn');
        const alertBox = $('#login-alert');
        
        // UI State: Loading
        btn.prop('disabled', true).text('Signing in...');
        alertBox.addClass('d-none');

        const email = $('#email').val();
        const password = $('#password').val();

        try {
            // Call Service
            const data = await AuthService.login(email, password);
            
            // Store Token for authenticated requests
            localStorage.setItem('access_token', data.access_token);
            
            // Redirect to Dashboard
            window.location.href = 'dashboard.html';
            
        } catch (error) {
            // Show Error
            alertBox.text(error).removeClass('d-none');
            btn.prop('disabled', false).text('Sign In');
        }
    });
});