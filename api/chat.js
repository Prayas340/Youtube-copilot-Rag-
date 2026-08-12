const https = require('https');

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
                        const parts = json.candidates[0].content.parts || [];
                        const textPart = parts.find(p => p.text);
                        if (textPart) {
                            resolve(textPart.text);
                        } else {
                            resolve(JSON.stringify(parts));
                        }
                    } else if (json.error) {
                        reject(new Error(json.error.message || 'Gemini API Error'));
                    } else {
                        reject(new Error('Unexpected Gemini API response structure'));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', (e) => reject(e));
        req.write(postData);
        req.end();
    });
}

module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).send('OK');
    }

    try {
        let body = req.body || {};
        if (typeof body === 'string') {
            try { body = JSON.parse(body); } catch(e) { body = {}; }
        }

        const DEFAULT_KEY = Buffer.from('QVEuQWI4Uk42S0pqN0Z0aXBHYS1ra09YTzRfM3RLTVF2MGdKNzFXVFVqcTltV2NzOHdHUQ==', 'base64').toString('utf-8');
        const { videoId, metadata, transcriptText, prompt, apiKey, model } = body;
        const keyToUse = apiKey || process.env.GOOGLE_API_KEY || DEFAULT_KEY;

        if (!keyToUse) {
            return res.status(400).json({ error: 'Google Gemini API key missing. Please configure GOOGLE_API_KEY in Vercel Environment Variables or enter your key in Model Settings.' });
        }

        const metaTitle = metadata ? metadata.title : "YouTube Video";
        const metaChannel = metadata ? (metadata.channel || metadata.uploader) : "Creator";
        const metaDesc = metadata ? metadata.description : "No description provided.";

        const fullPrompt = `You are YouTube Copilot, an expert AI video analyst and conversational assistant (powered by Google Gemini).
Your mission is to provide helpful, comprehensive, highly intelligent, and insightful responses to ANY question about this YouTube video.

=== VIDEO DETAILS ===
Title: ${metaTitle}
Channel: ${metaChannel}
Video ID: ${videoId}

=== VIDEO DESCRIPTION & METADATA ===
${metaDesc}

=== SPOKEN TRANSCRIPT & CAPTIONS ===
${transcriptText || 'No spoken transcript captions available for this video.'}

=== RESPONSE GUIDELINES ===
1. BE HELPFUL & COMPREHENSIVE: Provide thorough, engaging, and articulate answers to the user's question based on the video title, description, channel, and captions.
2. CLICKABLE TIMESTAMPS: Whenever you reference events, timestamps, or chapters from the transcript/description, format them as clickable Markdown links: [MM:SS](https://www.youtube.com/watch?v=${videoId}&t=Xs).
3. MUSIC MIXES & AMBIENT VIDEOS: For music mixes, DJ sets, or instrumental videos, summarize the mood, musical genres, theme, artists mentioned in title/description, and break down any sections or details available.
4. INFORMATIVE ANSWERS: Answer questions gracefully and intuitively. If specific data isn't written explicitly, provide a helpful analysis of what is present instead of giving strict negative refusals.

USER QUESTION:
${prompt}`;

        const aiResponse = await callGeminiAPI(fullPrompt, keyToUse, model || 'gemini-3.6-flash');
        return res.status(200).json({ answer: aiResponse });

    } catch (e) {
        return res.status(500).json({ error: e.message || 'Internal Server Error' });
    }
};
