/**
 * @author Eidan Khan
 */

let player;

function onYouTubeIframeAPIReady() {
    console.log("YouTube API Ready");
}

function extractVideoId(url) {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length == 11) ? match[7] : url;
}

$(document).ready(function () {
    const token = sessionStorage.getItem('access_token');
    if (!token) { window.location.href = 'login.html'; return; }

    $('#user-display-name').text(sessionStorage.getItem('name') || 'User');
    renderHistory();

    $('#fetch-btn').on('click', async function () {
        const rawInput = $('#video-id').val().trim();
        if (!rawInput) return;

        const videoId = extractVideoId(rawInput);
        const btn = $(this);

        // UI State: Loading
        btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');
        $('#result-workspace').removeClass('d-none');
        $('#loader-section').removeClass('d-none');
        $('#content-section').addClass('d-none');
        $('#video-player-section').addClass('d-none');

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/v1/transcripts?video_id=${videoId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const result = await response.json();

            if (response.ok) {
                $('#transcript-output').text(result.data.transcript);

                const formattedSrt = formatSrtTimestamps(result.data.transcript_with_timestamps);
                $('#timestamp-output').html(formattedSrt);

                initVideoPlayer(videoId);

                // UI State: Success
                $('#loader-section').addClass('d-none');
                $('#content-section').removeClass('d-none');
                $('#video-player-section').removeClass('d-none');

                addToHistory(videoId);
            } else {
                alert("Error fetching transcript.");
                $('#result-workspace').addClass('d-none');
            }
        } catch (error) {
            alert("Connection error to server.");
            $('#result-workspace').addClass('d-none');
        } finally {
            btn.prop('disabled', false).text("Extract");
        }
    });

    $(document).on('click', '.timestamp-link', function () {
        const seconds = $(this).data('seconds');
        if (player && player.seekTo) {
            player.seekTo(seconds, true);
            player.playVideo();
            $('html, body').animate({ scrollTop: $("#video-player-section").offset().top - 100 }, 500);
        }
    });

    $('#logout-btn').on('click', function () {
        sessionStorage.clear();
        window.location.href = 'login.html';
    });

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

function initVideoPlayer(videoId) {
    if (player) {
        player.loadVideoById(videoId);
    } else {
        player = new YT.Player('player', {
            height: '360',
            width: '640',
            videoId: videoId,
            playerVars: { 'rel': 0, 'showinfo': 0, 'modestbranding': 1 }
        });
    }
}

function formatSrtTimestamps(srtText) {
    return srtText.replace(/(\d{1,2}:\d{2}:\d{2})|(\d{1,2}:\d{2})/g, function (match) {
        const parts = match.split(':').reverse();
        let seconds = 0;
        seconds += parseInt(parts[0]);
        if (parts[1]) seconds += parseInt(parts[1]) * 60;
        if (parts[2]) seconds += parseInt(parts[2]) * 3600;
        return `<span class="timestamp-link" data-seconds="${seconds}">${match}</span>`;
    });
}

function addToHistory(videoId) {
    let history = JSON.parse(sessionStorage.getItem('transcripto_history') || "[]");
    history = history.filter(item => item !== videoId);
    history.unshift(videoId);
    if (history.length > 10) history.pop();
    sessionStorage.setItem('transcripto_history', JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    const history = JSON.parse(sessionStorage.getItem('transcripto_history') || "[]");
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