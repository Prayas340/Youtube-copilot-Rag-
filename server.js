const http = require('http');
const fs = require('fs');
const path = require('path');
const https = require('https');

const PORT = 8000;

try {
    const envPath = path.join(__dirname, '.env');
    if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf8');
        envContent.split(/\r?\n/).forEach(line => {
            const trimmed = line.trim();
            if (trimmed && !trimmed.startsWith('#')) {
                const [key, ...valueParts] = trimmed.split('=');
                if (key && valueParts.length > 0) {
                    process.env[key.trim()] = valueParts.join('=').trim();
                }
            }
        });
    }
} catch (e) {}

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

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
    urlOrId = urlOrId.trim();
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

    try {
        const oembedRaw = await httpGet(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`);
        const oembed = JSON.parse(oembedRaw);
        title = oembed.title || title;
        channel = oembed.author_name || channel;
    } catch (e) {}

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
        metadata: { title, channel, description },
        count: captions.length,
        transcript: captions
    };
}

function callGeminiAPI(prompt, apiKey, model = "gemini-3.6-flash") {
    return new Promise((resolve, reject) => {
        if (!model || model.includes("1.5") || model.includes("2.0") || model.includes("2.5")) {
            model = "gemini-3.6-flash";
        }

        const postData = JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.1, maxOutputTokens: 2048 }
        });

        const options = {
            hostname: 'generativelanguage.googleapis.com',
            port: 443,
            path: `/v1beta/models/${model}:generateContent?key=${apiKey}`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(body);
                    if (json.candidates && json.candidates[0] && json.candidates[0].content) {
                        resolve(json.candidates[0].content.parts[0].text);
                    } else if (json.error) {
                        reject(new Error(json.error.message || 'Gemini API Error'));
                    } else {
                        reject(new Error('Unexpected Gemini API response structure'));
                    }
                } catch (e) { reject(e); }
            });
        });

        req.on('error', (e) => reject(e));
        req.write(postData);
        req.end();
    });
}

function parseJsonBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk.toString());
        req.on('end', () => {
            try { resolve(body ? JSON.parse(body) : {}); } catch (e) { reject(e); }
        });
    });
}

const server = http.createServer(async (req, res) => {
    let reqUrl = req.url.split('?')[0];

    if (req.method === 'POST' && reqUrl === '/api/analyze') {
        try {
            const data = await parseJsonBody(req);
            const videoId = extractVideoId(data.youtubeUrl || '');
            if (!videoId) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                return res.end(JSON.stringify({ error: 'Invalid YouTube URL or Video ID' }));
            }
            const analysisResult = await analyzeYouTubeVideo(videoId);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(analysisResult));
        } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    if (req.method === 'POST' && reqUrl === '/api/chat') {
        try {
            const data = await parseJsonBody(req);
            const { videoId, metadata, transcriptText, prompt, apiKey, model } = data;
            const keyToUse = apiKey || process.env.GOOGLE_API_KEY;

            if (!keyToUse) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                return res.end(JSON.stringify({ error: 'Google Gemini API key missing.' }));
            }

            const metaTitle = metadata ? metadata.title : "YouTube Video";
            const metaChannel = metadata ? (metadata.channel || metadata.uploader) : "Creator";
            const metaDesc = metadata ? metadata.description : "No description provided.";

            const fullPrompt = `You are YouTube Copilot, an elite AI video assistant (powered by Google Gemini 3.5 Flash).
Your task is to answer ANY type of question about the YouTube video (Title: "${metaTitle}", ID: ${videoId}) like YouTube's "Ask Gemini" feature.

=== VIDEO METADATA & DESCRIPTION ===
Title: ${metaTitle}
Channel: ${metaChannel}
Full Description:
${metaDesc}

=== VIDEO CAPTIONS & TRANSCRIPT ===
${transcriptText || 'No spoken transcript captions available for this video.'}

USER QUESTION:
${prompt}`;

            const aiResponse = await callGeminiAPI(fullPrompt, keyToUse, model || 'gemini-3.5-flash');
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ answer: aiResponse }));
        } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    let filePath = path.join(__dirname, reqUrl === '/' ? 'index.html' : reqUrl);
    let extname = path.extname(filePath).toLowerCase();
    let contentType = MIME_TYPES[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 Page Not Found</h1>', 'utf-8');
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${error.code}`, 'utf-8');
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType, 'Cache-Control': 'no-cache' });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, () => {
    console.log(`🚀 YouTube Copilot Gemini 3.5 Flash Engine Live on port ${PORT}`);
});
