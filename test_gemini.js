const https = require('https');

const apiKey = process.env.GOOGLE_API_KEY;
const model = "gemini-3.5-flash";

if (!apiKey) {
    console.error("Please set GOOGLE_API_KEY environment variable.");
    process.exit(1);
}

const postData = JSON.stringify({
    contents: [{ parts: [{ text: "Hello! Summarize what AI is in one sentence." }] }]
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
        console.log("STATUS:", res.statusCode);
        console.log("RESPONSE BODY:", body);
    });
});

req.on('error', console.error);
req.write(postData);
req.end();
