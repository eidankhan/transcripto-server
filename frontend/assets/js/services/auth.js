/**
 * @author Eidan Khan
 */
const AuthService = {
    async signup(name, email, password) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await response.json();
        if (!response.ok) throw data.detail || "Signup failed";
        return data;
    },

    async verifyEmail(email, code) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/auth/verify-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        const data = await response.json();
        if (!response.ok) throw data.detail || "Verification failed";
        return data;
    },

    async resendCode(email) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/auth/resend-verification-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        if (!response.ok) throw "Failed to resend code";
        return true;
    },

    async login(email, password) {
        const response = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw data.detail || "Invalid email or password";
        }
        
        return data; // Returns { access_token: "...", token_type: "bearer" }
    }
};