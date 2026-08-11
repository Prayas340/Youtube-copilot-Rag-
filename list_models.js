const https = require('https');

const apiKey = process.env.GOOGLE_API_KEY;

if (!apiKey) {
    console.error("Please set GOOGLE_API_KEY environment variable.");
    process.exit(1);
}

https.get(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`, (res) => {
    let body = '';
    res.on('data', chunk => body += chunk);
    res.on('end', () => {
        try {
            const data = JSON.parse(body);
            if (data.models) {
                console.log("AVAILABLE MODELS:");
                data.models.forEach(m => console.log("-", m.name));
            } else {
                console.log("RESPONSE:", body);
            }
        } catch (e) {
            console.error(e);
        }
    });
}).on('error', console.error);
