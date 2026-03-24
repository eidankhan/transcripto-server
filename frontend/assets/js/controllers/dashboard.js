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
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    $('#fetch-btn').on('click', async function () {
        const rawInput = $('#video-id').val().trim();
        if (!rawInput) return;

        const videoId = extractVideoId(rawInput);
        const btn = $(this);

        btn.prop('disabled', true).text("...");
        // Ensure workspace is hidden while loading new data
        $('#result-workspace').addClass('d-none');

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/v1/transcripts?video_id=${videoId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const result = await response.json();

            if (response.ok) {
                $('#transcript-output').text(result.data.transcript);
                $('#timestamp-output').text(result.data.transcript_with_timestamps);

                // SHOW the workspace only now
                $('#result-workspace').removeClass('d-none');
            } else {
                alert("Error fetching transcript.");
            }
        } catch (error) {
            alert("Connection error.");
        } finally {
            btn.prop('disabled', false).text("Extract");
        }
    });

    $('#logout-btn').on('click', function () {
        localStorage.removeItem('access_token');
        window.location.href = 'login.html';
    });
});


function copyCurrentTab() {
    // 1. Identify which tab is currently visible to the user
    const isActivePlain = $('#plain-tab').hasClass('active');
    const targetId = isActivePlain ? '#transcript-output' : '#timestamp-output';

    // 2. Get the text content
    const textToCopy = $(targetId).text();

    if (!textToCopy) {
        alert("No text found to copy!");
        return;
    }

    // 3. Use the Clipboard API
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Visual feedback
        const originalBtnText = $('.card-footer .btn').text();
        $('.card-footer .btn').text('✅ Copied!').addClass('btn-success').removeClass('btn-outline-secondary');

        setTimeout(() => {
            $('.card-footer .btn').text(originalBtnText).addClass('btn-outline-secondary').removeClass('btn-success');
        }, 2000);
    }).catch(err => {
        console.error('Could not copy text: ', err);
        alert("Failed to copy. Please select and copy manually.");
    });
}