/* ==========================================================================
   UNIVERSAL INTERACTIVE JAVASCRIPT - YOUTUBE COPILOT WEB APP
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    
    const SAMPLE_VIDEOS = {
        "AlpvszL-CvR": {
            title: "Mastering AI Workflows in 2024",
            channel: "AI Engineers Lab",
            description: "Complete guide to setting up production AI workflows with vector databases and LLMs.\n00:00 - Intro\n04:05 - Vector Embeddings\n10:15 - Pipeline Automation"
        },
        "L_Guz73e6fw": {
            title: "LangChain RAG Architecture & VectorDBs",
            channel: "Tech Architecture Daily",
            description: "Deep dive into RAG architectures, history-aware retrievers, and vector memory."
        },
        "2X89y-ZcM1s": {
            title: "Gemini 2.0 Flash & Multimodal AI",
            channel: "DeepMind Highlights",
            description: "Exploring sub-second latency and 1M token context windows in Gemini 2.0."
        },
        "F4SYNSYKWMC": {
            title: "angelcore mix // DJ Anemia, VNXIOUS, LONOWN",
            channel: "VNXIOUS",
            description: "Curated aesthetic angelcore & breakcore music mix.\n00:00 - VNXIOUS - Angelic Reverie\n03:15 - DJ Anemia - Heavenly Glitch\n07:45 - LONOWN - Ethereal Echoes\n12:30 - VNXIOUS x DJ Anemia - Celestial Drift"
        }
    };

    let currentVideoId = null;
    let activeMetadata = null;
    let activeTranscriptData = [];

    // --- DOM ELEMENTS ---
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileSidebarCloseBtn = document.getElementById('mobile-sidebar-close-btn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const navLinks = document.querySelectorAll('.nav-link');
    const pageViews = document.querySelectorAll('.page-view');
    const pageTitleHeading = document.getElementById('page-title-heading');
    const youtubeUrlInput = document.getElementById('youtube-url-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const sampleChips = document.querySelectorAll('.sample-chip');
    const youtubePlayer = document.getElementById('youtube-player');
    const activeVideoTitle = document.getElementById('active-video-title');
    const videoIdBadge = document.getElementById('video-id-badge');
    const videoPlaceholderCard = document.getElementById('video-placeholder-card');
    const loadedVideoCard = document.getElementById('loaded-video-card');
    const chatContextTitle = document.getElementById('chat-context-title');
    const chatMessagesArea = document.getElementById('chat-messages-area');
    const chatInputField = document.getElementById('chat-input-field');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const micBtn = document.getElementById('mic-btn');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    const toastContainer = document.getElementById('toast-container');

    // --- 1. TOAST NOTIFICATIONS ---
    function showToast(message, icon = 'check_circle') {
        if (!toastContainer) {
            console.log(`[Notification]: ${message}`);
            return;
        }
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<span class="material-symbols-outlined" style="color: var(--primary-cyan);">${icon}</span><span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // --- MOBILE DRAWER NAVIGATION HANDLERS ---
    function openMobileSidebar() {
        document.body.classList.add('sidebar-mobile-open');
    }

    function closeMobileSidebar() {
        document.body.classList.remove('sidebar-mobile-open');
    }

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', openMobileSidebar);
    }
    if (mobileSidebarCloseBtn) {
        mobileSidebarCloseBtn.addEventListener('click', closeMobileSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeMobileSidebar);
    }

    // --- 2. VIEW NAVIGATION ---
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetView = link.getAttribute('data-view');
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            pageViews.forEach(view => {
                view.classList.remove('active');
                if (view.id === `view-${targetView}`) view.classList.add('active');
            });

            if (targetView === 'dashboard') pageTitleHeading.textContent = 'Universal Video Intelligence';
            if (targetView === 'model-settings') pageTitleHeading.textContent = 'Model & Engine Settings';

            // Close sidebar on mobile after clicking navigation item
            closeMobileSidebar();
        });
    });

    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', () => document.body.classList.toggle('sidebar-collapsed'));
    }

    if (themeToggleBtn) {
        let isDark = true;
        themeToggleBtn.addEventListener('click', () => {
            isDark = !isDark;
            document.body.classList.toggle('light-theme', !isDark);
            const icon = themeToggleBtn.querySelector('.material-symbols-outlined');
            if (icon) icon.textContent = isDark ? 'dark_mode' : 'light_mode';
            showToast(isDark ? 'Dark Obsidian Theme Enabled' : 'Light Theme Enabled', isDark ? 'dark_mode' : 'light_mode');
        });
    }

    function extractVideoId(urlOrId) {
        if (!urlOrId) return null;
        urlOrId = urlOrId.trim();
        if (/^[a-zA-Z0-9_-]{11}$/.test(urlOrId)) return urlOrId;
        const match = urlOrId.match(/(?:v=|\/shorts\/|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
        return match ? match[1] : null;
    }

    function seekToTimestamp(seconds) {
        if (youtubePlayer && youtubePlayer.contentWindow) {
            youtubePlayer.contentWindow.postMessage(JSON.stringify({
                event: 'command',
                func: 'seekTo',
                args: [seconds, true]
            }), '*');
            youtubePlayer.contentWindow.postMessage(JSON.stringify({
                event: 'command',
                func: 'playVideo',
                args: []
            }), '*');
        }
        showToast(`Seeking video to: ${formatSeconds(seconds)}`, 'schedule');
    }

    function formatSeconds(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // --- 3. VIDEO ANALYSIS PIPELINE ---
    async function loadAndAnalyzeVideo(youtubeUrl, customTitle = null) {
        const videoId = extractVideoId(youtubeUrl);
        if (!videoId) {
            showToast('Please enter a valid YouTube URL or Video ID', 'error');
            return;
        }

        currentVideoId = videoId;

        // Show loaded video card and hide placeholder card
        if (videoPlaceholderCard) videoPlaceholderCard.style.display = 'none';
        if (loadedVideoCard) loadedVideoCard.style.display = 'block';

        youtubePlayer.src = `https://www.youtube.com/embed/${videoId}?enablejsapi=1&autoplay=1`;
        activeVideoTitle.textContent = customTitle || `YouTube Video (${videoId})`;
        videoIdBadge.textContent = `ID: ${videoId}`;
        chatContextTitle.textContent = customTitle || `Video (${videoId})`;

        showToast('Extracting video metadata & description...', 'auto_awesome');

        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ youtubeUrl })
            });
            const data = await res.json();

            if (data.metadata) {
                activeMetadata = data.metadata;
                activeVideoTitle.textContent = data.metadata.title;
                chatContextTitle.textContent = data.metadata.title;
            }

            if (data.transcript && data.transcript.length > 0) {
                activeTranscriptData = data.transcript;
                showToast(`Acquired ${data.transcript.length} transcript captions!`, 'check_circle');
            } else {
                activeTranscriptData = [];
                showToast('AI Multimodal Video Engine Ready (Music / Uncaptioned Video)', 'auto_awesome');
            }

        } catch (e) {
            console.warn('Backend server API call failed, using fallback mode:', e);
            useSampleFallback(videoId, customTitle);
        }
    }

    function useSampleFallback(videoId, customTitle) {
        const fallback = SAMPLE_VIDEOS[videoId] || {
            title: customTitle || `YouTube Video (${videoId})`,
            channel: "YouTube Creator",
            description: "No metadata description available."
        };

        activeMetadata = fallback;
        activeVideoTitle.textContent = fallback.title;
        chatContextTitle.textContent = fallback.title;
    }

    function attachTimestampListeners() {
        document.querySelectorAll('.timestamp-btn').forEach(btn => {
            btn.onclick = () => {
                const seconds = parseInt(btn.getAttribute('data-time'), 10);
                seekToTimestamp(seconds);
            };
        });
    }
    attachTimestampListeners();

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            const url = youtubeUrlInput ? youtubeUrlInput.value.trim() : '';
            if (!url) {
                showToast('Please paste a YouTube URL to analyze', 'warning');
                return;
            }
            loadAndAnalyzeVideo(url);
        });
    }

    if (youtubeUrlInput) {
        youtubeUrlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const url = youtubeUrlInput.value.trim();
                if (url) loadAndAnalyzeVideo(url);
            }
        });
    }

    if (sampleChips) {
        sampleChips.forEach(chip => {
            chip.addEventListener('click', () => {
                sampleChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                const videoId = chip.getAttribute('data-video-id');
                const title = chip.getAttribute('data-title');
                if (youtubeUrlInput) youtubeUrlInput.value = `https://www.youtube.com/watch?v=${videoId}`;
                loadAndAnalyzeVideo(videoId, title);
            });
        });
    }

    // --- 4. REAL GEMINI AI CHAT ENGINE ---
    async function sendChatMessage(userText) {
        if (!userText.trim()) return;

        if (!currentVideoId) {
            showToast('Please paste a YouTube URL or click a sample video first!', 'warning');
            return;
        }

        // Remove Animated Empty State Card if present
        const emptyState = document.getElementById('chat-empty-state');
        if (emptyState) {
            emptyState.style.opacity = '0';
            emptyState.style.transform = 'translateY(-10px)';
            setTimeout(() => emptyState.remove(), 250);
        }

        // Append User Message
        const userRow = document.createElement('div');
        userRow.className = 'message-row user';
        userRow.innerHTML = `<div class="chat-bubble">${escapeHtml(userText)}</div>`;
        if (chatMessagesArea) chatMessagesArea.appendChild(userRow);

        if (chatInputField) chatInputField.value = '';
        if (chatMessagesArea) chatMessagesArea.scrollTop = chatMessagesArea.scrollHeight;

        // Append Typing Indicator
        const typingRow = document.createElement('div');
        typingRow.className = 'message-row ai';
        typingRow.id = 'typing-indicator-row';
        typingRow.innerHTML = `
            <div class="chat-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        if (chatMessagesArea) chatMessagesArea.appendChild(typingRow);
        if (chatMessagesArea) chatMessagesArea.scrollTop = chatMessagesArea.scrollHeight;

        const transcriptTextToPass = activeTranscriptData.length > 0 
            ? activeTranscriptData.map(item => `[${item.formatted_time}] ${item.text}`).join('\n')
            : "[No spoken transcript captions available. Use video description and metadata]";

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    videoId: currentVideoId,
                    metadata: activeMetadata,
                    transcriptText: transcriptTextToPass,
                    prompt: userText,
                    model: 'gemini-3.6-flash'
                })
            });

            const data = await res.json();
            typingRow.remove();

            if (data.answer) {
                const aiRow = document.createElement('div');
                aiRow.className = 'message-row ai';
                aiRow.innerHTML = `
                    <div class="chat-bubble">
                        ${convertMarkdownToHtml(data.answer)}
                        <div class="sources-accordion" style="margin-top: 14px;">
                            <button class="sources-toggle">
                                <span class="material-symbols-outlined" style="font-size: 14px;">expand_more</span>
                                <span>🔍 View Context Sources</span>
                            </button>
                            <div class="sources-content">
                                <p>Video Metadata & Description + Captions (ID: ${currentVideoId})</p>
                            </div>
                        </div>
                    </div>
                `;
                if (chatMessagesArea) chatMessagesArea.appendChild(aiRow);
                if (chatMessagesArea) chatMessagesArea.scrollTop = chatMessagesArea.scrollHeight;
                attachTimestampListeners();
                attachSourcesToggle();
            } else {
                showToast(data.error || 'Failed to generate answer', 'error');
            }

        } catch (e) {
            typingRow.remove();
            showToast('API Connection Error', 'error');
        }
    }

    function convertMarkdownToHtml(text) {
        // Convert Markdown timestamp links with t=XXs parameter
        let html = text.replace(/\[(\d{1,2}:\d{2}(?::\d{2})?)\]\([^\)]*?t=(\d+)s?[^\)]*?\)/g, (match, timeStr, seconds) => {
            return `<button class="timestamp-btn" data-time="${seconds}"><span class="material-symbols-outlined" style="font-size: 12px;">schedule</span> ${timeStr}</button>`;
        });
        // Convert Markdown timestamp links without explicit seconds param or plain timestamps [MM:SS]
        html = html.replace(/\[(\d{1,2}:\d{2}(?::\d{2})?)\](?!\()/g, (match, timeStr) => {
            const parts = timeStr.split(':').map(Number);
            let seconds = 0;
            if (parts.length === 3) seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
            else if (parts.length === 2) seconds = parts[0] * 60 + parts[1];
            return `<button class="timestamp-btn" data-time="${seconds}"><span class="material-symbols-outlined" style="font-size: 12px;">schedule</span> ${timeStr}</button>`;
        });
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    function escapeHtml(text) {
        return text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m]));
    }

    if (sendChatBtn) sendChatBtn.addEventListener('click', () => sendChatMessage(chatInputField ? chatInputField.value : ''));
    if (chatInputField) chatInputField.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendChatMessage(chatInputField.value); });

    if (suggestionBtns) {
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => sendChatMessage(btn.getAttribute('data-prompt')));
        });
    }

    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            if (chatMessagesArea) {
                chatMessagesArea.innerHTML = `
                    <div class="chat-empty-state" id="chat-empty-state">
                        <div class="empty-state-badge">
                            <span class="material-symbols-outlined" style="font-size: 18px; color: var(--primary-cyan);">auto_awesome</span>
                            <span>AI Copilot Ready</span>
                        </div>
                        <h3 class="empty-state-title">Ask Any Question About Your Video</h3>
                        <p class="empty-state-subtitle">Paste a YouTube link above, then ask any type of question to analyze tracklists, tutorials, podcasts, or key moments.</p>
                    </div>
                `;
            }
            showToast('Chat history cleared', 'delete_sweep');
        });
    }

    let isListening = false;
    if (micBtn) {
        micBtn.addEventListener('click', () => {
            isListening = !isListening;
            micBtn.style.color = isListening ? 'var(--primary-cyan)' : 'var(--text-muted)';
            if (isListening) {
                showToast('Voice Mic Activated - Listening...', 'mic');
                if (chatInputField) chatInputField.placeholder = "Listening...";
                setTimeout(() => {
                    if (chatInputField) {
                        chatInputField.value = "Explain the key steps or tracklist in this video.";
                        chatInputField.placeholder = "Ask anything about this video...";
                    }
                    micBtn.style.color = 'var(--text-muted)';
                    isListening = false;
                }, 2500);
            }
        });
    }

    function attachSourcesToggle() {
        document.querySelectorAll('.sources-toggle').forEach(toggle => {
            toggle.onclick = () => {
                const content = toggle.nextElementSibling;
                if (content) {
                    content.classList.toggle('open');
                    const icon = toggle.querySelector('.material-symbols-outlined');
                    if (icon) icon.textContent = content.classList.contains('open') ? 'expand_less' : 'expand_more';
                }
            };
        });
    }

});
