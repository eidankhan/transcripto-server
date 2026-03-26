/**
 * @author Eidan Khan
 * adminController.js - Refactored for External Auth Flow
 */
const adminController = {
    avgChart: null,
    dauChart: null,

    /**
     * Entry point: Checks authorization and either renders or redirects
     */
    init() {
        if (adminService.isAuthorized()) {
            this.renderDashboard();
        } else {
            // If not authorized, redirect to the main login page
            console.warn("Unauthorized access attempt to Admin. Redirecting...");
            window.location.href = 'login.html';
        }
    },

    /**
     * Main orchestration: Refreshes analytics and user list
     */
    async renderDashboard(range = 'monthly') {
        const wrapper = document.getElementById('adminWrapper');
        if (wrapper) wrapper.classList.remove('d-none');

        // 1. Fetch & Render Analytics Data
        const data = await adminService.getFullDashboardData(range);
        if (data) {
            this.updateKPIs(data);
            this.updateOrRenderAvgUsage(data.engagement.usageTrend);
            this.renderDauTrend(data.engagement.usageTrend);
        }

        // 2. Fetch & Render User Management Table
        await this.refreshUsers();
    },

    /**
     * Updates the top-level metric cards
     */
    updateKPIs(data) {
        // 1. Standard Stats
        document.getElementById('stat-total-users').innerText = data.totals.users;
        document.getElementById('stat-total-transcripts').innerText = data.totals.transcripts;
        document.getElementById('stat-avg-sessions').innerText = data.totals.sessions;

        // 2. Guest & Lead Stats (Mapping to your specific JSON keys)
        const guestTranscriptsEl = document.getElementById('stat-guest-transcripts');
        if (guestTranscriptsEl) {
            guestTranscriptsEl.innerText = data.totals.guest_transcripts;
        }

        const anonUsersEl = document.getElementById('stat-anon-users');
        if (anonUsersEl) {
            anonUsersEl.innerText = data.totals.anonymous_users;
        }

        const powerGuestsEl = document.getElementById('stat-power-guests');
        if (powerGuestsEl) {
            powerGuestsEl.innerText = data.totals.power_guests;
        }

        // 3. Stickiness
        const ratio = data.engagement.stickiness || 0;
        document.getElementById('stickiness-ratio').innerText = ratio + '%';
        document.getElementById('stickiness-bar').style.width = ratio + '%';
    },

    /**
     * User Management: Fetching
     */
    async refreshUsers() {
        const token = sessionStorage.getItem('access_token');
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/admin/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) this.logout();
                throw new Error("Failed to fetch users");
            }

            const users = await response.json();
            this.renderUserTable(users);
        } catch (err) {
            console.error("User Fetch Error:", err);
        }
    },

    /**
     * User Management: Rendering
     */
    renderUserTable(users) {
        const tbody = document.getElementById('user-table-body');
        if (!tbody) return;

        tbody.innerHTML = '';
        if (!users || users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No users found.</td></tr>`;
            return;
        }

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><div class="fw-bold text-dark">${user.name}</div></td>
                <td>${user.email}</td>
                <td class="small text-muted">${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <span class="badge ${user.is_verified ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning'} rounded-pill px-3">
                        ${user.is_verified ? 'Verified' : 'Pending'}
                    </span>
                </td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3" 
                            onclick="adminController.deleteUser(${user.id})">
                        Delete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    },

    /**
     * User Management: Deleting
     */
    async deleteUser(userId) {
        if (!confirm(`Permanently delete User #${userId}?`)) return;

        const token = sessionStorage.getItem('access_token');
        try {
            const resp = await fetch(`${CONFIG.API_BASE_URL}/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (resp.ok) {
                await this.renderDashboard();
            } else {
                const error = await resp.json();
                alert(`Error: ${error.detail || "Action failed"}`);
            }
        } catch (err) {
            console.error("Delete Error:", err);
        }
    },

    /**
     * Charting: Usage Range Change
     */
    async changeRange(range) {
        const data = await adminService.getFullDashboardData(range);
        if (data) {
            this.updateOrRenderAvgUsage(data.engagement.usageTrend);
            const label = document.getElementById('usage-label');
            if (label) label.innerText = `Avg Transcripts per User (${range})`;
        }
    },

    /**
     * Charting: Bar Chart
     */
    updateOrRenderAvgUsage(data) {
        const ctx = document.getElementById('avgUsageChart').getContext('2d');
        if (this.avgChart) {
            this.avgChart.data.labels = data.labels;
            this.avgChart.data.datasets[0].data = data.values;
            this.avgChart.update();
        } else {
            this.avgChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{ label: 'Transcripts', data: data.values, backgroundColor: '#6610f2', borderRadius: 8 }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }
    },

    /**
     * Charting: Line Chart
     */
    renderDauTrend(data) {
        const canvas = document.getElementById('dauTrendChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (this.dauChart) this.dauChart.destroy();

        this.dauChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    borderColor: '#0d6efd',
                    fill: true,
                    backgroundColor: 'rgba(13, 110, 253, 0.05)',
                    tension: 0.4,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: true, grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f0f0f0' } }
                }
            }
        });
    },

    logout() {
        adminService.logout();
    }
};

document.addEventListener('DOMContentLoaded', () => adminController.init());