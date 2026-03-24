/**
 * @author Eidan Khan
 */

function extractVideoId(url) {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length == 11) ? match[7] : url;
}

$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    if (!token) { window.location.href = 'login.html'; return; }

    $('#user-display-name').text(localStorage.getItem('user_name') || 'User');
    renderHistory();

    $('#fetch-btn').on('click', async function () {
        const rawInput = $('#video-id').val().trim();
        if (!rawInput) return;

        const videoId = extractVideoId(rawInput);
        const btn = $(this);

        btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');
        $('#result-workspace').addClass('d-none');

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/v1/transcripts?video_id=${videoId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const result = await response.json();

            if (response.ok) {
                $('#transcript-output').text(result.data.transcript);
                $('#timestamp-output').text(result.data.transcript_with_timestamps);
                $('#result-workspace').removeClass('d-none');
                
                // Intelligent History Management
                addToHistory(videoId);
            } else {
                alert("Error fetching transcript. Please check the URL.");
            }
        } catch (error) {
            alert("Connection error to server.");
        } finally {
            btn.prop('disabled', false).text("Extract");
        }
    });

    // Logout
    $('#logout-btn').on('click', function () {
        localStorage.clear();
        window.location.href = 'login.html';
    });

    // Tab Switching
    $(document).on('click', '#transcriptTabs .nav-link', function (e) {
        e.preventDefault();
        $('#transcriptTabs .nav-link').removeClass('active');
        $(this).addClass('active');
        $('.tab-pane').removeClass('show active');
        const target = $(this).data('bs-target');
        $(target).addClass('show active');
        $('#download-btn').text($(this).attr('id') === 'plain-tab' ? "Download .txt" : "Download .srt");
    });
});

// History Logic
function addToHistory(videoId) {
    let history = JSON.parse(localStorage.getItem('transcripto_history') || "[]");
    // Move to top if exists, else add new
    history = history.filter(item => item !== videoId);
    history.unshift(videoId);
    // Keep only last 10 items
    if (history.length > 10) history.pop();
    localStorage.setItem('transcripto_history', JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    const history = JSON.parse(localStorage.getItem('transcripto_history') || "[]");
    const list = $('#history-list');
    list.empty();

    if (history.length === 0) {
        list.append('<div class="p-4 text-muted small">No recent extractions</div>');
        return;
    }

    history.forEach(id => {
        list.append(`
            <button class="history-item" onclick="loadFromHistory('${id}')">
                <i class="bi bi-clock-history"></i>
                <span class="text-truncate">Video: ${id}</span>
            </button>
        `);
    });
}

function loadFromHistory(id) {
    $('#video-id').val(`https://www.youtube.com/watch?v=${id}`);
    $('#fetch-btn').trigger('click');
}

function downloadCurrentTab() {
    const isPlain = $('#plain-tab').hasClass('active');
    const content = isPlain ? $('#transcript-output').text() : $('#timestamp-output').text();
    if (!content) return;

    const videoId = extractVideoId($('#video-id').val()) || "transcript";
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Transcripto_${videoId}.${isPlain ? 'txt' : 'srt'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function copyCurrentTab() {
    const isPlain = $('#plain-tab').hasClass('active');
    const content = isPlain ? $('#transcript-output').text() : $('#timestamp-output').text();
    if (content) {
        navigator.clipboard.writeText(content).then(() => alert("Copied!"));
    }
}