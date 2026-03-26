const guestController = {
    async fetchFree() {
        const urlInput = document.getElementById('video-url').value;
        const resultArea = document.getElementById('guest-result-area');
        const contentDiv = document.getElementById('guest-content');
        const loader = document.getElementById('guest-loader');

        if (!urlInput) return alert("Please paste a YouTube URL");

        // Show UI
        resultArea.classList.remove('d-none');
        loader.classList.remove('d-none');
        contentDiv.innerText = '';

        try {
            // Extract Video ID from URL
            const videoId = this.extractVideoId(urlInput);
            
            // API Call (No Authorization Header = Guest)
            const response = await fetch(`${CONFIG.API_BASE_URL}/v1/transcripts?video_id=${videoId}`);
            const result = await response.json();

            loader.classList.add('d-none');

            if (response.status === 200) {
                contentDiv.innerText = result.data.transcript;
                this.updateUsageHint();
            } else if (response.status === 403) {
                // Limit hit! Show Modal
                const limitModal = new bootstrap.Modal(document.getElementById('limitModal'));
                limitModal.show();
            } else {
                contentDiv.innerHTML = `<p class="text-danger">Error: ${result.message}</p>`;
            }
        } catch (error) {
            loader.classList.add('d-none');
            console.error("Guest Fetch Error:", error);
        }
    },

    extractVideoId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }
};

// Event Listeners
document.getElementById('guest-fetch-btn').addEventListener('click', () => guestController.fetchFree());