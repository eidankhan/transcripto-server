const adminService = {
    async getFullDashboardData(range = 'monthly') {
        const token = sessionStorage.getItem('access_token');
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/stats?range=${range}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.status === 401 || response.status === 403) return this.logout();
        return await response.json();
    },

    async getUsers() {
        const token = sessionStorage.getItem('access_token');
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.status === 401 || response.status === 403) return this.logout();
        return await response.json();
    },

    isAuthorized() {
        const token = sessionStorage.getItem('access_token');
        const role = sessionStorage.getItem('user_role');
        return !!token && role === 'ADMIN';
    },

    logout() {
        sessionStorage.clear();
        window.location.href = 'login.html';
    }
};