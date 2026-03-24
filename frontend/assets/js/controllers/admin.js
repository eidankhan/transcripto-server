/**
 * @author Eidan Khan
 */
/**
 * @author Eidan Khan
 */
$(document).ready(function () {
    const token = localStorage.getItem('access_token');

    // ONLY check for the token. Ignore roles for now.
    if (!token) {
        console.warn("No token found. Redirecting to login.");
        window.location.replace('login.html');
        return;
    }

    // If a token exists, just let the page load.
    console.log("Token verified. Loading Admin Panel...");
    initGrowthChart();
    fetchUsers();
});

async function fetchUsers() {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const users = await response.json();

        renderUserTable(users);
        $('#total-users').text(users.length);
    } catch (err) {
        console.error("Failed to fetch users", err);
    }
}

function renderUserTable(users) {
    const tbody = $('#user-table-body');
    tbody.empty();

    users.forEach(user => {
        tbody.append(`
            <tr>
                <td class="fw-bold">${user.name}</td>
                <td>${user.email}</td>
                <td class="small text-muted">${new Date(user.created_at).toLocaleDateString()}</td>
                <td><span class="badge bg-success">Active</span></td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUser('${user.id}')">Delete</button>
                </td>
            </tr>
        `);
    });
}

async function deleteUser(userId) {
    if (!confirm("Are you sure you want to delete this user?")) return;

    const token = localStorage.getItem('access_token');
    try {
        const resp = await fetch(`${CONFIG.API_BASE_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resp.ok) fetchUsers();
    } catch (err) { alert("Delete failed"); }
}

function initGrowthChart() {
    const ctx = document.getElementById('growthChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'New Users',
                data: [12, 19, 3, 5], // This should eventually come from an API
                borderColor: '#4f46e5',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(79, 70, 229, 0.1)'
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}