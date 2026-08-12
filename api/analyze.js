const https = require('https');

function httpGet(url) {
    return new Promise((resolve, reject) => {
        https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' } }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(body));
        }).on('error', reject);
    });
}

function extractVideoId(urlOrId) {
    if (!urlOrId) return null;
    urlOrId = String(urlOrId).trim();
    if (/^[a-zA-Z0-9_-]{11}$/.test(urlOrId)) return urlOrId;
    const match = urlOrId.match(/(?:v=|\/shorts\/|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
}

function parseXmlCaptions(xml) {
    const items = [];
    const regex = /<text start="([\d.]+)"[^>]*>(.*?)<\/text>/g;
    let match;
    while ((match = regex.exec(xml)) !== null) {
        const start = parseFloat(match[1]);
        const rawText = match[2]
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&#39;/g, "'")
            .replace(/&quot;/g, '"')
            .replace(/<[^>]+>/g, '')
            .trim();

        if (rawText) {
            const mins = Math.floor(start / 60);
            const secs = Math.floor(start % 60);
            const formatted_time = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            items.push({
                start: Math.floor(start),
                formatted_time,
                text: rawText
            });
        }
    }
    return items;
}

async function analyzeYouTubeVideo(videoId) {
    let title = `YouTube Video (${videoId})`;
    let channel = "YouTube Creator";
    let description = "No video description available.";
    let captions = [];

    // 1. oEmbed metadata
    try {
        const oembedRaw = await httpGet(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`);
        const oembed = JSON.parse(oembedRaw);
        title = oembed.title || title;
        channel = oembed.author_name || channel;
    } catch (e) {}

    // 2. Fetch Watch Page & Captions
    try {
        const html = await httpGet(`https://www.youtube.com/watch?v=${videoId}`);
        const match = html.match(/ytInitialPlayerResponse\s*=\s*({.+?});/);
        if (match) {
            const playerResponse = JSON.parse(match[1]);
            if (playerResponse.videoDetails) {
                title = playerResponse.videoDetails.title || title;
                channel = playerResponse.videoDetails.author || channel;
                description = playerResponse.videoDetails.shortDescription || description;
            }
            const captionTracks = playerResponse.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
            if (captionTracks.length > 0) {
                const xml = await httpGet(captionTracks[0].baseUrl);
                captions = parseXmlCaptions(xml);
            }
        }
    } catch (e) {}

    return {
        video_id: videoId,
        metadata: {
            title,
            channel,
            description
        },
        count: captions.length,
        transcript: captions
    };
}

function sendResponse(res, statusCode, data) {
    res.statusCode = statusCode;
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(data));
}

module.exports = async (req, res) => {
    if (req.method === 'OPTIONS') {
        res.statusCode = 200;
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        return res.end();
    }

    try {
        let body = req.body || {};
        if (typeof body === 'string') {
            try { body = JSON.parse(body); } catch(e) { body = {}; }
        }

        const youtubeUrl = body.youtubeUrl || (req.query ? req.query.youtubeUrl : '') || '';
        const videoId = extractVideoId(youtubeUrl);

        if (!videoId) {
            return sendResponse(res, 400, { error: 'Invalid YouTube URL or Video ID' });
        }

        const result = await analyzeYouTubeVideo(videoId);
        return sendResponse(res, 200, result);
    } catch (e) {
        return sendResponse(res, 500, { error: e.message || 'Internal Server Error' });
    }
};
