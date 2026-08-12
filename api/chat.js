const https = require('https');

function callGeminiAPI(prompt, apiKey, model = "gemini-1.5-flash") {
    return new Promise((resolve, reject) => {
        if (!model || model.includes("3.5") || model.includes("3.1")) {
            model = "gemini-1.5-flash";
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

        const { videoId, metadata, transcriptText, prompt, apiKey, model } = body;
        const keyToUse = apiKey || process.env.GOOGLE_API_KEY;

        if (!keyToUse) {
            return sendResponse(res, 400, { error: 'Google Gemini API key missing. Please configure GOOGLE_API_KEY in Vercel Environment Variables.' });
        }

        const metaTitle = metadata ? metadata.title : "YouTube Video";
        const metaChannel = metadata ? (metadata.channel || metadata.uploader) : "Creator";
        const metaDesc = metadata ? metadata.description : "No description provided.";

        const fullPrompt = `You are YouTube Copilot, an elite AI video assistant (powered by Google Gemini).
Your task is to answer ANY type of question about the YouTube video (Title: "${metaTitle}", ID: ${videoId}) like YouTube's "Ask Gemini" feature.

=== VIDEO METADATA & DESCRIPTION ===
Title: ${metaTitle}
Channel: ${metaChannel}
Full Description:
${metaDesc}

=== VIDEO CAPTIONS & TRANSCRIPT ===
${transcriptText || 'No spoken transcript captions available for this video.'}

=== STRICT ANSWERING RULES ===
1. ANSWER ANY QUESTION: Provide direct, thorough, comprehensive, and high-intelligence answers to ANY question asked about this video's content, concepts, arguments, code, speakers, or topics.
2. CLICKABLE TIMESTAMPS: Always include clickable Markdown timestamp links using format: [MM:SS](https://www.youtube.com/watch?v=${videoId}&t=Xs) whenever referencing key events, timestamps, quotes, or chapters.
3. MUSIC MIXES & TRACKLISTS: Inspect the FULL DESCRIPTION field first for tracklists. If no tracklist exists in the description or captions, state: "No written tracklist was found in the video metadata." DO NOT invent fake song names.
4. NO HALLUCINATIONS: If the question answer is not present in either the description or transcript, explicitly state: "The video description and captions do not contain this information."

USER QUESTION:
${prompt}`;

        const aiResponse = await callGeminiAPI(fullPrompt, keyToUse, model || 'gemini-1.5-flash');
        return sendResponse(res, 200, { answer: aiResponse });

    } catch (e) {
        return sendResponse(res, 500, { error: e.message || 'Internal Server Error' });
    }
};
