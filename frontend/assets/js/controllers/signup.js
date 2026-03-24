/**
 * @author Eidan Khan
 */
$(document).ready(function() {
    let userEmail = "";

    // 1. Initial Signup
    $('#signup-form').on('submit', async function(e) {
        e.preventDefault();
        const btn = $('#signup-btn');
        setLoading(btn, true, "Creating...");

        const name = $('#name').val();
        const email = $('#email').val();
        const password = $('#password').val();

        try {
            await AuthService.signup(name, email, password);
            userEmail = email;
            
            // UI Transition
            $('#display-email').text(email);
            $('#signup-form').addClass('hidden');
            $('#verify-form').removeClass('hidden');
            $('#login-link-text').addClass('hidden');
            $('#header-slogan').text("Enter the 6-digit code sent to your email.");
            
            showSuccess("Account created! Please verify.");
        } catch (err) {
            showError(err);
        } finally {
            setLoading(btn, false, "Create Account");
        }
    });

    // 2. Verification
    $('#verify-form').on('submit', async function(e) {
        e.preventDefault();
        const btn = $('#verify-btn');
        setLoading(btn, true, "Verifying...");

        const code = $('#code').val();

        try {
            await AuthService.verifyEmail(userEmail, code);
            showSuccess("Success! Redirecting...");
            setTimeout(() => window.location.href = 'login.html', 1500);
        } catch (err) {
            showError(err);
        } finally {
            setLoading(btn, false, "Verify & Login");
        }
    });

    // 3. Helpers
    function setLoading(btn, isLoading, text) {
        btn.prop('disabled', isLoading).text(text);
    }

    function showError(msg) {
        $('#error-alert').text(msg).removeClass('hidden');
        $('#success-alert').addClass('hidden');
    }

    function showSuccess(msg) {
        $('#success-alert').text(msg).removeClass('hidden');
        $('#error-alert').addClass('hidden');
    }
});