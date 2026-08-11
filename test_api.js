const http = require('http');

function postJson(url, data) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(data);
        const req = http.request(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(JSON.parse(body)));
        });
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

async function testApi() {
    try {
        console.log("Querying Gemini AI chat via server...");
        const chatRes = await postJson('http://localhost:8000/api/chat', {
            videoId: 'L_Guz73e6fw',
            metadata: { title: 'Sam Altman Podcast', channel: 'Lex Fridman', description: 'Lex Fridman Podcast with Sam Altman' },
            transcriptText: '[00:15] Sam Altman speaks about AI models and GPT-4.',
            prompt: 'What does Sam Altman speak about?',
            model: 'gemini-3.5-flash'
        });

        console.log("SERVER RESPONSE OBJECT:", chatRes);

    } catch (e) {
        console.error("Test Error:", e.message);
    }
}

testApi();
