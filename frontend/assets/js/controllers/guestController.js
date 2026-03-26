const guestController = {
    async fetchFree() {
        const urlInput = document.getElementById('video-url').value;
        const resultArea = document.getElementById('guest-result-area');
        const loader = document.getElementById('guest-loader');

        // Target the two new content containers
        const contentPlain = document.getElementById('guest-content-plain');
        const contentTime = document.getElementById('guest-content-time');

        if (!urlInput) {
            alert("Please paste a YouTube URL");
            return;
        }

        const videoId = this.extractVideoId(urlInput);
        if (!videoId) {
            alert("Invalid YouTube URL. Please try again.");
            return;
        }

        // --- UI Setup ---
        resultArea.classList.remove('d-none');
        loader.classList.remove('d-none');

        // Hide content panes while loading
        contentPlain.innerText = '';
        contentTime.innerText = '';
        document.getElementById('guestTabContent').classList.add('d-none');

        try {
            // API Call (No Auth Header = Treated as Guest by Backend)
            const response = await fetch(`${CONFIG.API_BASE_URL}/v1/transcripts?video_id=${videoId}`);
            const result = await response.json();

            loader.classList.add('d-none');

            if (response.status === 200) {
                // 1. Populate both views
                contentPlain.innerText = result.data.transcript;
                contentTime.innerText = result.data.transcript_with_timestamps;

                // 2. Show the content and reset to the first tab (Clean Text)
                document.getElementById('guestTabContent').classList.remove('d-none');
                this.resetToFirstTab();

                // 3. Scroll result into view for better UX
                resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            } else if (response.status === 403) {
                // Limit hit (5/5 requests used)
                resultArea.classList.add('d-none');
                const limitModal = new bootstrap.Modal(document.getElementById('limitModal'));
                limitModal.show();
            } else if (response.status === 404) {
                // Video has no transcripts
                contentPlain.innerHTML = `
                    <div class="text-center p-4">
                        <i class="bi bi-exclamation-circle fs-2 text-warning"></i>
                        <p class="mt-2 mb-0">${result.message || "No transcripts found for this video."}</p>
                    </div>`;
                document.getElementById('guestTabContent').classList.remove('d-none');
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            loader.classList.add('d-none');
            console.error("Guest Fetch Error:", error);
            alert("Connection error. Is the server running?");
        }
    },

    extractVideoId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    },

    resetToFirstTab() {
        const firstTabEl = document.querySelector('#guest-plain-tab');
        if (firstTabEl) {
            const firstTab = new bootstrap.Tab(firstTabEl);
            firstTab.show();
        }
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const fetchBtn = document.getElementById('guest-fetch-btn');
    if (fetchBtn) {
        fetchBtn.addEventListener('click', () => guestController.fetchFree());
    }

    // Allow "Enter" key to trigger fetch
    const urlInput = document.getElementById('video-url');
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') guestController.fetchFree();
        });
    }
});